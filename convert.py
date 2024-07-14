import sys, os
import re
import argparse
import yaml
import toml
from pathlib import Path
from datetime import datetime

class ParserState:
    UNKNOWN = 0
    FRONT_MATTER = 1
    CONTENT = 2

class Parser:
    def __init__(self, file_path):
        self.file_path = file_path
        self.state = ParserState.UNKNOWN
        self.raw_front = []
        self.front = None
        self.content = []

    def read(self):
        with open(self.file_path, 'r', encoding='utf-8') as file:
            for line in file:
                if self.state == ParserState.UNKNOWN and line.strip() == "---":
                    self.state = ParserState.FRONT_MATTER
                elif self.state == ParserState.FRONT_MATTER and line.strip() == "---":
                    self.state = ParserState.CONTENT
                elif self.state == ParserState.FRONT_MATTER:
                    self.raw_front.append(line)
                elif self.state == ParserState.CONTENT:
                    self.content.append(line)

        self.front = yaml.safe_load(''.join(self.raw_front))
        return self

    def into_jekyll(self):
        if self.front:
            return JekyllDoc(self.front, ''.join(self.content), str(self.file_path))
        return None

class JekyllDoc:
    def __init__(self, front, content, path:str=None):
        self.front = JekyllFront(**front)
        self.content = content

        # Extract date from file path
        self.extract_date(path)

    def extract_date(self, path):
        match = re.search(r'\d{4}-\d{2}-\d{2}', path)
        if match:
            self.front.date = match.group(0)

    @staticmethod
    def open_file(file_path):
        parser = Parser(file_path)
        parser.read()
        return parser.into_jekyll()

class JekyllFront:
    def __init__(self, title, 
                 date=None, subtitle=None, author=None, tags=None, 
                 **extra):
        self.title = title
        self.date = date
        self.subtitle = subtitle
        self.author = author
        self.tags = tags

        self.extra = extra

    def to_zola_front(self):
        if 'layout' in self.extra:
            del self.extra['layout']
        if 'header-img' in self.extra:
            self.extra['cover'] = self.extra.pop('header-img')
        taxonomies = {}
        if self.tags:
            taxonomies["tags"] = self.tags
        if self.author:
            taxonomies["author"] = self.author if isinstance(self.author,list) else [self.author]
            
        return ZolaFront(
            title=self.title,
            date=datetime.strptime(self.date, '%Y-%m-%d').date() if self.date else None,
            description=self.subtitle,
            author=self.author,
            extra=self.extra,
            taxonomies = taxonomies
        )

class ZolaFront:
    def __init__(self, title, date, description, author, extra=None, taxonomies=None):
        self.title = title
        self.date = date
        self.description = description
        self.author = author
        self.extra = extra
        self.taxonomies = taxonomies

    def to_toml(self):
        data = {
            "title": self.title,
            "date": self.date.isoformat() if self.date else None,
            "description": self.description,
        }
        if self.taxonomies:
            data.update({'taxonomies': self.taxonomies})
        if self.extra:
            data.update({'extra': self.extra})
        toml_data = toml.dumps(data).strip()
        toml_data = re.sub(r'\[\s*([^\]]+?)\s*,\s*\]', r'[\1]', toml_data)
        return f"{toml_data}\n"

class ZolaDoc:
    def __init__(self, front, content):
        self.front = front
        self.content = content

    def to_string(self):
        return f"+++\n{self.front.to_toml()}+++\n\n{self.content}"

def convert_file(in_path, out_path):
    in_path = Path(in_path)
    jekyll_doc = JekyllDoc.open_file(in_path)
    if jekyll_doc:
        zola_front = jekyll_doc.front.to_zola_front()
        zola_doc = ZolaDoc(zola_front, jekyll_doc.content)
        os.makedirs(out_path, exist_ok=True)
        if os.path.isdir(out_path):
            out_path = os.path.join(out_path, in_path.name)
        else:
            out_path = Path(out_path)
        with open(out_path,'w',encoding='utf-8') as file:
            file.write(zola_doc.to_string())
    else:
        print("Error: Could not parse the Jekyll document.", file=sys.stderr)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--inpath","-i", default=
                        r'..\\hibikilogy.github.io\\_posts\\', 
                        help="input dir or file")
    parser.add_argument("--outpath","-o", default=
                        r'../v2-dev/content/content', 
                        help="output dir or file")
    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    if os.path.isfile(args.inpath):
        convert_file(args.inpath, args.outpath)
    elif os.path.isdir(args.inpath):
        for root, dirs, filenames in os.walk(args.inpath):
            for filename in filenames:
                if filename.endswith(('.md')):
                    filepath = os.path.join(root, filename)
                    convert_file(filepath, args.outpath)
    else:
        print("Error: No input file provided.", file=sys.stderr)

if __name__ == "__main__":
    main()
