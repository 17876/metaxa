from metaxa.metaxa import WAVMetadata
from utils.utils import get_creation_date
import os


def metadata_ucs_rename(directory, ext):
    """
    Takes a path and renames all the files with a given extension based on their metadata,
    following the usc naming standard.
    """
    for filename in os.listdir(directory):
        filepath = os.path.join(directory, filename)
        if os.path.splitext(filename)[1].lower() == ext.lower():
            try:
                extractor = WAVMetadata(filepath)
                metadata = extractor.extract()

                # ucs category id
                cat_id = metadata.get('INFO', {}).get('IGNR', 'NONE')

                # generating FXName
                # keywords = metadata.get('INFO', {}).get('IKEY', 'NONE').split(';')
                # keywords_stripped = [i.strip() for i in keywords]
                # fx_name = '-'.join(keywords_stripped)
                fx_name = metadata.get('INFO', {}).get('INAM', 'NONE')

                # creator id
                creator_id = 'AX'

                # source id
                source_id = metadata.get('INFO', {}).get('IPRD', 'NONE')

                # unique identifier to avoid duplicates
                # date-time
                # date is the date of the creation YYYYMMDD
                # time is the time in HHMMSS

                # retrieving the date
                (date, time) = get_creation_date(filepath)
                date_concat = date.replace('-', '')
                time_concat = time.replace('-', '')
                user_data = '-'.join([date_concat, time_concat])

                ucs_filename = f"{'_'.join([cat_id, fx_name, creator_id, source_id, user_data])}{os.path.splitext(filename)[1]}"

                ucs_filepath = os.path.join(directory, ucs_filename)

                os.rename(filepath, ucs_filepath)
                print(f"Renamed: {filename} -> {ucs_filename}")

            except Exception as e:
                print(f"Error processing {filename}: {e}")