import os
import sys
import argparse
import logging
from http.client import responses

from processing_modes.modes import process_volumes, process_chapters, process_hybrid

logger = logging.getLogger("MangaPDFConverter")

def main():
    parser = argparse.ArgumentParser(description="bulk convert manga images into pdf files",
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""example usage:
                                     python3 main.py /path/to/manga --mode volumes
                                     python3 main.py /path/to/manga --mode chapters
                                     python3 main.py /path/to/manga --mode hybrid
                                     """)

    parser.add_argument("path", help='top level folder containing all chapter/volume folders of a specific manga')
    parser.add_argument("--mode", choices=['volumes', 'chapters', 'hybrid'],default='hybrid',  help='the processing mode (default = hybrid)')
    parser.add_argument('--delete_images',action='store_true',help='delete the source images after conversion')
    parser.add_argument('--debug', action='store_true',help='enables debug logging')

    args = parser.parse_args()

    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',)

    logger.info(f"---mangaPDFconverter---")
    logger.info(f"path: {args.path}")
    logger.info(f"mode: {args.mode}")
    logger.info(f"delete images: {args.delete_images}")
    logger.info(f"debug: {args.debug}")

    if not os.path.isdir(args.path):
        logger.error(f"path: {args.path} does not exist")
        sys.exit(1)

    if args.delete_images:
        print("⚠️ WARNING: images files and empty directory will be deleted after conversion!")
        response=input("are you sure you want to continue? (y/n): ")
        if response.lower() not in ['y', 'yes']:
            logger.info("operation cancelled by user")
            sys.exit(0)

    try:
        if args.mode == 'volumes':
            process_volumes(args.path, args.delete_images)
        elif args.mode == 'chapters':
            process_chapters(args.path, args.delete_images)
        else:
            process_hybrid(args.path, args.delete_images)

        logger.info(f"manga: {args.path} conversion completed successfully!")
    except Exception as e:
        logger.error(f"fatal error during processing: {e}")
        sys.exit(1)



if __name__ == '__main__':
    main()

