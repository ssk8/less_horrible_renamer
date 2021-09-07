import argparse
import os
import re


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--torrent_header', default='[] ')
    parser.add_argument('-p', '--path', default='/home/pi/')
    parser.add_argument('-i', '--input_dir', default='downloads')
    parser.add_argument('-o', '--output_dir', default='downloads/tvshows')
    parser.add_argument('-n', '--not_a_test', action='store_true')
    parser.add_argument('-d', '--dont_move', action='store_true')
    return parser.parse_args()


def find_files(home, input_dir, header):
    file_list = [f for f in os.listdir(os.path.join(home, input_dir)) if
            f.startswith(header) and f.endswith('.mkv' or '.mp4' or '.avi')]
    return sorted(file_list)


def get_new_name(old_name, header):
    current_name = old_name.replace(header, '')
    season_search = re.search("S[0-9]{1,2} ", current_name)
    if season_search:
        current_season = current_name[season_search.start()+1]
        current_name = current_name.replace(' S{}'.format(current_season), '')
    else:
        current_season = 1
    name_index = re.search(r" - [0-9]{1,2} [\[, (]", current_name).start()
    current_dir_name = current_name[0:name_index]
    current_name = '{} - S0{}E{}'.format(current_name[:name_index], current_season, current_name[name_index + 3:])
    return current_name, current_dir_name


def check_dir(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)


def main():
    cli_args = get_args()
    path, input_dir, output_dir = cli_args.path, cli_args.input_dir, cli_args.output_dir
    t_header = cli_args.torrent_header

    print('File name header: "{}"\n'.format(t_header))
    files = find_files(path, input_dir, t_header)

    if not cli_args.dont_move:
        check_dir(os.path.join(path, output_dir))

    for file in files:
        new_file_name, new_dir_name = get_new_name(file, t_header)
        new_dir = os.path.join(path, output_dir, new_dir_name) if not cli_args.dont_move else os.path.join(path, input_dir)
        print('OLD: {}\nNEW: "{}"\n    in "{}"\n'.format(file, new_file_name, new_dir))

        if cli_args.not_a_test:
            check_dir(new_dir)
            os.rename(os.path.join(path, input_dir, file), os.path.join(new_dir, new_file_name))

    if not cli_args.not_a_test:
        print('***This was just a test! use "-n" flag to write***')


if __name__ == "__main__":
    main()
