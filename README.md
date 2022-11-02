# AutoSub
Automatically subtitle a video from almost any language to your native language with at least 70% of precision.

## Setup
Just clone this repository, run `python -r requeriments.txt` to install dependences and then you already can use it.

## Usage and Resources
This script has support for a lot of languages, take a look in `python main.py --languages` to see all supported languages or `python main.py --has-lang japan` to search for a especific country.

You can use the script by passing the video path to script:
```bash
python main.py -f ~/Desktop/my_personal_show_eps1.mp4
```

You also can set a from_language (video) and to_language (srt). If you no set langs then the default is from japanese to portuguese for now.

```bash
python main.py --file ~/Desktop/my_anime_eps1.mp4 --from-language ja --to-language en
```

The script will generate files into tmp folder inside projet. First create a .wav file with audio of video, then analisys and create separeted chunks of each non-silence detection. Now we check each chunk, recognize if there is speak, translate to target language and then finally write it on srt file.

After copy the srt and finish with it, you can cleanup the tmp folder easly just run
```bash
python main.py --cleanup
```

## TO-DO
Here I'm separating the to-do list that still need work on

Fixes
- Improve the voice recognize (currently the precision is just around 50%)
- Small texts for a very fast time instead showing a whole sentence for few seconds
- Huge texts at once for long time instead showing slowly parts of text in small times

Features
- Merge speech recognition support with translate support. [List of supported languages on speech_recognition](https://stackoverflow.com/a/14302134/17274446)

## Contribute

You can contribue with this project, just fork it, make a branch and open a PR.

## Authors

* [Diogo Fernandes](https://github.com/dfop02)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
