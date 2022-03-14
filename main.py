from argparse import ArgumentParser
from auto_sub import AutoSub

parser = ArgumentParser()
parser.add_argument("-f", "--file", dest="filename",
                    help="write report to FILE", metavar="FILE", required=True)
parser.add_argument("--from-language",
                    dest="from_language",
                    help="Video language")
parser.add_argument("--to-language",
                    dest="to_language",
                    help="Subtitle language")
parser.add_argument("-q", "--quiet",
                    action="store_false", dest="verbose", default=False,
                    help="don't print status messages to stdout")

args = parser.parse_args()

auto_sub = AutoSub(args.filename)
auto_sub.generate_subtitles()
