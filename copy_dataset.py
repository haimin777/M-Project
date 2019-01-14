import argparse
import pandas as pd
import os
import shutil as sh
import errno

parser = argparse.ArgumentParser()
parser.add_argument('-o','--open-file', help='Path to csv with IDs', required=False)
parser.add_argument('-t','--target-path', help='Path where to copy', required=False)


def get_paths():

    # get df with paths and convert it to paths|IDs format

    if os.path.isfile(os.path.join(os.getcwd(), 'paths.csv')):
        print('\n file with paths detected', '\n'*2)

        df = pd.read_csv('paths.csv')
        df['ID'] = df.paths.str.split('\\', expand=True)[8]
        print(df.head(2))
        return df
    else:
        print('file with paths not detected!')


def read_ids(args):
    # get ids to dataframe to list for future filtering

    if os.path.isfile(os.path.join(os.getcwd(), args.open_file)):
        print('get file with IDs OK')

        return pd.read_csv(args.open_file, header=None)[0].astype('str').tolist()


def filter_and_copy(df, ids, args):
    # drop rows that not in filter list(ids)

    df = df[df.ID.isin(ids)]
    #print(':-)'*10, df.size)
    for i, path in enumerate(df.paths):
        dest = os.path.join(args.target_path, path.split('\\')[-1])
        if i%50 ==0:
            print(i, path, '\n', dest)
        try:
            sh.copytree(path, dest)
        except OSError as e:
            # If the error was caused because the source wasn't a directory
            if e.errno == errno.ENOTDIR:
                sh.copy(path, dest)
            else:
                print('Directory not copied. Error: %s' % e)


'''

args = parser.parse_args()
a = args.open_file
df = pd.read_csv(a, header=None)
#print(df.head())

df = df[0][int(args.number_strings):]
df.to_csv(a, sep='\n', index=None)
'''

if __name__ == '__main__':

    df = get_paths()
    args = parser.parse_args()
    filt_list = read_ids(args)
    #print('\n', len(filt_list))
    filter_and_copy(df=df, ids=filt_list, args=args)
