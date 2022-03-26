import os, glob, shutil
from argparse import ArgumentParser
from auto_sub import AutoSub, show_suported_languages

parser = ArgumentParser()

parser.add_argument("-f", "--file",
                    dest="filename",
                    help="write report to FILE",
                    metavar="FILE",
                    required=False)

parser.add_argument("--languages",
                    dest="languages",
                    action="store_true",
                    help="print available languages")

parser.add_argument("--has-lang",
                    dest="has_lang",
                    type=str,
                    help="print if the given country has language support")

parser.add_argument("--from-language",
                    dest="from_language",
                    help="Video language")

parser.add_argument("--to-language",
                    dest="to_language",
                    help="Subtitle language")

parser.add_argument("--srt-path",
                    dest="srt_path",
                    type=str,
                    help="Path to save srt instead of tmp folder")

parser.add_argument("-c", "--cleanup",
                    dest="cleanup",
                    action="store_true",
                    help="clean tmp folder")

parser.add_argument("-q", "--quiet",
                    dest="verbose",
                    action="store_false",
                    help="don't print status messages to stdout")

args = parser.parse_args()

if args.filename:
    auto_sub = AutoSub(args.filename, verbose=args.verbose)
    auto_sub.generate_subtitles()

elif args.cleanup:
    files = glob.glob('tmp/*')
    for file in files:
        if os.path.isfile(file):
            os.remove(file)
        else:
            shutil.rmtree(file)

elif args.languages:
    show_suported_languages()

elif args.has_lang:
    show_suported_languages(args.has_lang)

else:
    print('Unknown params, please try again. Check -h for help.')
