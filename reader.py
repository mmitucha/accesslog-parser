#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import os
import json
import datetime


class History(object):
    """
    Class for manipulating history data of the file, that will be followed"
    """ 
    def __init__(self):
        self.__base_dir = os.path.dirname(os.path.abspath(__file__))
        self.depth = 10
        self.file_path = os.path.join(self.__base_dir, 'reading_state.json')

        try:
            self.last = self.get_last()
        except IOError:
            self.last = False
            self.all = {}


    def get_last(self):
        # Return last(chronologically) history entry
        with open(self.file_path, 'r') as __file:
                self.all = json.load(__file)

        if isinstance(self.all, dict):
            now = datetime.datetime.now().isoformat()
            latest = None
            for i,k in self.all.iteritems():
                if latest == None:
                    latest = i
                else:
                    if i > latest:
                        latest = i
                    else:
                        continue
            return self.all[latest]


    def del_oldest(self):
        # Delete oldest(chronologicaly) history entry
        if isinstance(self.all, dict):
            while (len(self.all) + 1 ) > self.depth:
                now = datetime.datetime.now().isoformat()
                oldest = None
                for i,k in self.all.iteritems():
                    if oldest == None:
                        oldest = i
                    else:
                        if i < oldest:
                            oldest = i
                        else:
                            continue

                if oldest in self.all:
                        self.all.pop(oldest)
                else:
                    print("Can't delete old history records.")
        else:
            print("History file not in proper format")


    def save_new(self, start, end, file_ino, file_path):
        # Save new history entry
        new_record = {
                        'inode': file_ino,
                        'file': file_path,
                        'seek_start': start,
                        'seek_end': end,
                 }            
        now = datetime.datetime.now().isoformat()
        self.all[now] = new_record

        with open(self.file_path, 'w') as __file:
            json.dump(self.all, __file, encoding="utf-8", indent=4, separators=(',', ': '))


class Read(object):
    """
    Class for reading lines from followed file.
    """
    def __init__(self, follow):
        # self.lines = []
        self.follow = follow


    def read(self, status_save=True):
        # Initializes 'History' class as 'Read' class attribute, to group 
        # history file related functions under 'history' attribute.
        self.history = History()   

        # File that will be read from.
        self.__follow_ino = int(os.stat(self.follow).st_ino)

        if self.history.last:
            if self.history.last['inode'] == self.__follow_ino:
                self.__seek_start = self.history.last['seek_end']
            else:
                self.__seek_start = 0
        else:
            self.history.last = False
            self.__seek_start = 0

        with open(self.follow, 'r') as file_:
            file_.seek(self.__seek_start)
            # Writes this line to private 'self.__lines' attribute.
            self.__lines = self.__stream_lines(file_)    
            self.__seek_end = file_.tell()

        if status_save == True:
            self.history.save_new(
                                    start=self.__seek_start, 
                                    end=self.__seek_end, 
                                    file_ino=self.__follow_ino, 
                                    file_path=self.follow
                                    )
        return self.__lines


    def __stream_by_line(self, file_):
        # Get line from file (generator)
        while True:
            line = file_.readline()
            if not line:
                break
            yield line


    def __stream_lines(self, file_, how_much=None):
        """
        Stream all lines from 'f'(file) attribute.
        Uses '__stream_by_line' generator to get lines.
        If 'how_much' attribute set, will stream only that much lines, 
        otherwise will stream until 'StopIteration' exception (end of file) 
        will be raise.
        """
        try:
            get_line = self.__stream_by_line(file_)
            lines = []
            if isinstance(how_much, int):
                n = 0
                while n < how_much:
                    lines.append(next(get_line))
                    n += 1
                return lines
            else:
                while 1:
                    lines.append(next(get_line))
        except StopIteration:
            return lines
