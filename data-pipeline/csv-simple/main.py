#!/usr/bin/env python
import argparse
import logging
import os
import time

from config import INPUT_DIR, LOG_FORMAT
from src import extractors
from src.extractors import Extractor
from src.loaders import Loader
from src.processors import Processor


def main(log, input_dir, file_path=None):

    # extract
    if file_path:
        log.info(f'scanning file_path={file_path}')
        file_paths = [file_path]
    else:
        log.info(f'scanning input_dir={input_dir}')
        file_paths = extractors.scan_input_dir(input_dir)
    data_cache = []
    if file_paths:
        for file_path in file_paths:
            extractor = Extractor.get_instance(file_path)
            if not extractor:
                log.warning(f'could not extract {file_path}')
                continue
            data_item = extractor.extract()
            if not data_item:
                log.error(f'error extracting {file_path}')
                continue
            data_cache.extend(data_item)

    # transform
    log.info(f'processing data cache size={len(data_cache)}')
    if not data_cache:
        logging.info('nothing extracted')
    else:
        payload = []
        for item in data_cache:
            file_type = item['file_type']
            processor = Processor.get_instance(file_type)
            if not processor:
                log.error(f'could not process file type {file_type}')
                continue
            processed = processor.process(item['data'])
            if processed:
                payload.append(dict(data=processed, file_type=file_type, file=item['file']))
            else:
                log.error(f'could not process processed={processed} item={item}')

        # load
        log.info(f'loading payload size={len(payload)}')
        if not payload:
            log.error('no payload')
            return
        Loader().dump(payload)
    log.info('completed')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--file-path',
        default=None,
        help='Run file at file path through data pipeline (default=%(default)s).')
    parser.add_argument(
        '-i', '--input-dir',
        default=INPUT_DIR,
        help='Run files in directory through data pipeline (default=%(default)s).')
    parser.add_argument(
        '-t', '--time-period',
        default=60,
        help='Seconds to wait between scans of input directory (default=%default)s).')
    args = parser.parse_args()

    # start up
    logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)
    logger = logging.getLogger('pipeline')
    logger.info('start')
    logger.debug(f'args={args}')
    if args.file_path:
        main(log=logger, input_dir=args.input_dir, file_path=args.file_path)
    else:
        if not (os.path.exists(args.input_dir) and os.path.isdir(args.input_dir)):
            logger.error(f"input dir '{args.input_dir}' does not exist or is not a directory")
            exit(1)
        while True:
            main(log=logger, input_dir=args.input_dir)
            time.sleep(args.time_period)
