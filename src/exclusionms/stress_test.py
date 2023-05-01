import argparse
import asyncio
import datetime
import logging
import multiprocessing
import signal
import time
from multiprocessing import Queue
from queue import Empty

import exclusionms.random
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
import numpy as np
from . import apihandler
from .components import DynamicExclusionTolerance

stop_requested = False

def random_point(charge_range, mass_range, rt_range, ook0_range, intensity_range):
    return exclusionms.random.generate_random_point(charge_range=charge_range, mass_range=mass_range, rt_range=rt_range,
                                                    ook0_range=ook0_range, intensity_range=intensity_range)


def random_interval(dynamic_tolerance, charge_range, mass_range, rt_range, ook0_range, intensity_range):
    return exclusionms.random.generate_random_interval(dynamic_tolerance, interval_id=None, charge_range=charge_range,
                                                       mass_range=mass_range, rt_range=rt_range,
                                                       ook0_range=ook0_range, intensity_range=intensity_range)


def signal_handler(signum, frame, process):
    global stop_requested
    stop_requested = True
    print("\nStopping gracefully. Please wait...")
    process.terminate()
    process.join()


def calculate_mass(mz: float, charge: int) -> float:
    return mz * charge - charge * 1.00727647


def add_intervals(exclusion_api_ip, exclusion_intervals, n_intervals, interval_time):
    for i in range(n_intervals):
        apihandler.add_intervals(exclusion_api_ip=exclusion_api_ip, exclusion_intervals=exclusion_intervals)
        time.sleep(interval_time)


async def update_plot(query_time, elapsed_time, x_data, y_data, line, ax, interval_queue, realtime_plot=False):
    x_data.append(query_time)
    y_data.append(elapsed_time)

    # Calculate the running average time
    window_size = 20  # Set the window size for the running average
    if len(y_data) >= window_size:
        running_average = np.convolve(y_data, np.ones(window_size) / window_size, mode='valid')
        avg_line, = ax.plot(x_data[:len(running_average)], running_average, color='red', linestyle='--')

    try:
        while True:
            interval_time = interval_queue.get_nowait()
            ax.axvline(interval_time, color='green', linestyle='--', alpha=0.5)
    except Empty:
        pass

    line.set_xdata(x_data)
    line.set_ydata(y_data)
    ax.relim()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    ax.autoscale_view()

    # Create custom legend elements
    legend_elements = [
        Line2D([0], [0], color='red', linestyle='--', lw=2, label=f'Running Average [window_size: {window_size}]'),
        mpatches.Patch(facecolor='green', edgecolor='green', alpha=0.5, linestyle='--',
                       label='Interval Addition Event'),
        mpatches.Patch(facecolor='orange', edgecolor='orange', alpha=0.5, linestyle='--',
                       label='Duty Cycle Impact Limit'),
        Line2D([0], [0], color='blue', linestyle='-', lw=2, label='Raw Query Time'),
    ]

    # Add the legend to the plot
    ax.legend(handles=legend_elements, loc='upper left')

    if realtime_plot is True:
        plt.draw()
        plt.pause(0.001)


def add_additional_intervals(exclusion_api_ip, num_additional_intervals, additional_interval_delay, dynamic_tolerance,
                             interval_queue, charge_range, mass_range, rt_range, ook0_range, intensity_range):
    while not stop_requested:
        intervals = [random_interval(dynamic_tolerance, charge_range, mass_range, rt_range, ook0_range, intensity_range)
                     for i in range(num_additional_intervals)]
        apihandler.add_intervals(exclusion_api_ip=exclusion_api_ip, exclusion_intervals=intervals)
        interval_queue.put(datetime.datetime.now())  # Put the current datetime into the queue
        time.sleep(additional_interval_delay)


def main(args):
    title = f"ExclusionMS Size: {args.num_intervals}, Num Points: {args.num_points}, Query Delay: {args.point_delay}, " \
            f"Additional Intervals: {args.num_additional_intervals}, Interval Delay: {args.additional_interval_delay}"
    file_name = title.replace(':', '_').replace(',', '_').replace(' ', '')
    csv_file = file_name + '.csv'

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    log = logging.getLogger(__name__)

    signal.signal(signal.SIGINT, lambda s, f: signal_handler(s, f, p))
    global stop_requested

    logging.info('Clearing Intervals')
    apihandler.clear(exclusion_api_ip=args.exclusion_api_ip)

    dynamic_tolerance = DynamicExclusionTolerance(charge=args.charge_tolerance,
                                                  mass=args.mass_tolerance,
                                                  rt=args.rt_tolerance,
                                                  ook0=args.ook0_tolerance,
                                                  intensity=args.intensity_tolerance)

    # Preload Intervals
    if args.num_intervals > 0:

        log.info(f'Adding {args.num_intervals} random intervals')
        intervals = [
            random_interval(dynamic_tolerance, args.charge_range, args.mass_range, args.rt_range, args.ook0_range,
                            args.intensity_range) for i in range(args.num_intervals)]
        apihandler.add_intervals(exclusion_api_ip=args.exclusion_api_ip, exclusion_intervals=intervals)

        # Wait for intervals to be fully processed
        for i in range(10):
            exclusionms_len = apihandler.get_len(exclusion_api_ip=args.exclusion_api_ip)
            if exclusionms_len == args.num_intervals:
                break

            log.info(f'ExclusionMS still processing intervals... {exclusionms_len} / {args.num_intervals}')
            time.sleep(1)

        time.sleep(2)

    if args.realtime_plot is True:
        plt.ion()
    fig, ax = plt.subplots(figsize=(15, 5))
    x_data, y_data = [], []
    line, = ax.plot(x_data, y_data, color='blue')

    ax.set_xlabel('Time of Query Execution')
    ax.set_ylabel('Query Processing Time (s)')
    ax.axhline(0.1, color='orange', linestyle='--', alpha=0.5)

    ax.set_title(title)

    interval_queue = Queue()

    p = None  # Declare p here so it can be accessed later
    if args.num_additional_intervals > 0:
        log.info('Starting additional interval adder process')
        p = multiprocessing.Process(target=add_additional_intervals,
                                    args=(args.exclusion_api_ip, args.num_additional_intervals,
                                          args.additional_interval_delay, dynamic_tolerance, interval_queue,
                                          args.charge_range, args.mass_range, args.rt_range, args.ook0_range,
                                          args.intensity_range))
        p.start()

    # Query Points
    start_time_global = time.time()

    # Query Points
    log.info('Starting query point loop')
    percents = []
    while not stop_requested:
        points = [random_point(args.charge_range, args.mass_range, args.rt_range, args.ook0_range, args.intensity_range)
                  for i in range(args.num_points)]

        current_time = time.time()
        if current_time - start_time_global >= args.run_time:
            log.info(f"Stopping after {args.run_time} seconds of operation.")
            break

        start_time = time.time()
        exclusions = apihandler.exclusion_search_points(exclusion_api_ip=args.exclusion_api_ip, exclusion_points=points)
        percent_excluded = len([e for e in exclusions if e is True]) / len(exclusions)
        percents.append(percent_excluded)
        log.info(f'excluded: {round(percent_excluded * 100, 2)}% of the queried points')
        elapsed_time = time.time() - start_time
        asyncio.run(update_plot(datetime.datetime.now(), elapsed_time, x_data, y_data, line, ax, interval_queue,
                                args.realtime_plot))
        time.sleep(args.point_delay)

    if p and p.is_alive():
        p.terminate()  # Terminate the process if it's still running

    if args.realtime_plot is True:
        plt.ioff()
        plt.show()

    log.info(f'Saving Figure to: {csv_file}')
    plt.figtext(0.5, 0.01, f'{str(np.mean(percents) * 100)}', wrap=True, horizontalalignment='center', fontsize=10)
    fig.savefig(csv_file, dpi=300, bbox_inches='tight')

    log.info('Clearing Intervals')
    apihandler.clear(exclusion_api_ip=args.exclusion_api_ip)

    log.info('Done!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ExclusionMS real-time plotting script.')

    # Stress Tests Arguments
    parser.add_argument('--exclusion_api_ip', type=str, default='http://127.0.0.1:8000',
                        help='IP address of the ExclusionMS server.')
    parser.add_argument('--num_intervals', type=int, default=100000,
                        help='Number of intervals to add.')
    parser.add_argument('--point_delay', type=float, default=0.1,
                        help='Time in seconds between adding points.')
    parser.add_argument('--num_points', type=float, default=1000,
                        help='Number of points to search per query')
    parser.add_argument('--num_additional_intervals', type=int, default=100,
                        help='Additional intervals to add during runtime')
    parser.add_argument('--additional_interval_delay', type=float, default=1,
                        help='Additional intervals to add during runtime')
    parser.add_argument('--run_time', type=float, default=30,
                        help='Length of time to run the stress test for.')
    parser.add_argument('--realtime_plot', type=bool, default=True,
                        help='plot stress test data in real time')

    # Random Arguments
    parser.add_argument('--charge_range', metavar=('MIN', 'MAX'), type=int, nargs=2, default=[1, 5],
                        help='range of charges (default: 1 to 5)')
    parser.add_argument('--mass_range', metavar=('MIN', 'MAX'), type=float, nargs=2, default=[500.0, 700.0],
                        help='range of masses (default: 500 to 5000)')
    parser.add_argument('--rt_range', metavar=('MIN', 'MAX'), type=float, nargs=2, default=[0.0, 1000.0],
                        help='range of retention times (default: 0 to 10000)')
    parser.add_argument('--ook0_range', metavar=('MIN', 'MAX'), type=float, nargs=2, default=[0.5, 1.5],
                        help='range of OOK0 values (default: 0.5 to 1.5)')
    parser.add_argument('--intensity_range', metavar=('MIN', 'MAX'), type=float, nargs=2, default=[500.0, 50000.0],
                        help='range of intensities (default: 500 to 50000)')

    # Tolerance Arguments
    parser.add_argument('--charge_tolerance', type=bool, default=False,
                        help='charge tolerance value (default: False)')
    parser.add_argument('--mass_tolerance', type=float, default=5,
                        help='mass tolerance value (default: 5)')
    parser.add_argument('--rt_tolerance', type=float, default=100,
                        help='retention time tolerance value (default: 1000)')
    parser.add_argument('--ook0_tolerance', type=float, default=None,
                        help='OOK0 tolerance value (default: None)')
    parser.add_argument('--intensity_tolerance', type=float, default=None,
                        help='intensity tolerance value (default: None)')
    args = parser.parse_args()

    main(args)
