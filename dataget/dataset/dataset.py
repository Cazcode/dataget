#!/usr/bin/env python
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xefc95f2a

# Compiled with Coconut version 1.2.3 [Colonel]

# Coconut Header: --------------------------------------------------------

from __future__ import print_function, absolute_import, unicode_literals, division

import sys as _coconut_sys, os.path as _coconut_os_path
_coconut_file_path = _coconut_os_path.dirname(_coconut_os_path.abspath(__file__))
_coconut_sys.path.insert(0, _coconut_file_path)
from __coconut__ import _coconut, _coconut_MatchError, _coconut_tail_call, _coconut_tco, _coconut_igetitem, _coconut_compose, _coconut_pipe, _coconut_starpipe, _coconut_backpipe, _coconut_backstarpipe, _coconut_bool_and, _coconut_bool_or, _coconut_minus, _coconut_map, _coconut_partial
from __coconut__ import *
_coconut_sys.path.remove(_coconut_file_path)

# Compiled Coconut: ------------------------------------------------------

import os
import shutil
from abc import ABCMeta
from abc import abstractmethod
from abc import abstractproperty
from copy import copy
import pandas as pd
import numpy as np


def merge(*datasets, **kwargs):

    if len(datasets) < 2:
        raise Exception("Please merge atleast 2 datasets, got {}".format(len(datasets)))

# get subsets
    training_sets = (list)((_coconut.functools.partial(map, _coconut.operator.attrgetter("training_set")))(datasets))
    test_sets = (list)((_coconut.functools.partial(map, _coconut.operator.attrgetter("test_set")))(datasets))

# load subsets
    for set in training_sets + test_sets:
        set._load_dataframe(**kwargs)

# get dataframes
    df_train = (_coconut_partial(pd.concat, {}, 1, axis=0))((list)((_coconut.functools.partial(map, _coconut.operator.attrgetter("_dataframe")))(training_sets)))
    df_test = (_coconut_partial(pd.concat, {}, 1, axis=0))((list)((_coconut.functools.partial(map, _coconut.operator.attrgetter("_dataframe")))(test_sets)))

# get base class copy
    base_dataset = (copy)(datasets[0])
    base_dataset.training_set._dataframe = df_train
    base_dataset.test_set._dataframe = df_test

#reset state
    base_dataset._complete_set = None

    return base_dataset





class DataSet(object):
    __metaclass__ = ABCMeta

    def __init__(self, name, home_path, train_prop=0.8):
        self.name = name
        self.path = os.path.join(home_path, self.name)

        self.train_prop = train_prop
        self._dataframe = None
        self._complete_set = None
        self._test_set = None
        self._training_set = None


    @property
    def complete_set(self):

        if self._complete_set is None:
            self._load_dataframe()

        return self._complete_set


    def make_dirs(self):
        if not os.path.exists(self.path):
            os.makedirs(self.path)


    def before_op(self, **kwargs):
        pass


    def get(self, download=True, rm=False, rm_compressed=True, process=True, rm_raw=True, **kwargs):
        self.before_op(**kwargs)

# rm
        if rm:
            self.rm(**kwargs)

# return if path exists, dataset downloaded already, else create path
        if not self.is_empty():
            return self

# get data
        if download:
            self.download(**kwargs)

        self.extract(**kwargs)

# process
        if process:
            self.process(**kwargs)

            if rm_raw:
                self.rm_raw(**kwargs)

# clean
        if rm_compressed:
            self.rm_compressed(**kwargs)

        return self




    def download(self, rm=False, **kwargs):
        self.before_op(**kwargs)
        print("===DOWNLOAD===")

# rm
        if rm:
            self.rm(**kwargs)

        if not self.is_empty():
            return self


        self.make_dirs()

        self._download(**kwargs)

        print("")

        return self

    def extract(self, **kwargs):
        self.before_op(**kwargs)

        print("===EXTRACT===")

        self.make_dirs()

        self._extract(**kwargs)

        print("")

        return self

    def rm_compressed(self, **kwargs):
        self.before_op(**kwargs)
        print("===RM-COMPRESSED===")

        self._rm_compressed(**kwargs)

        print("")

        return self

    def process(self, **kwargs):
        self.before_op(**kwargs)

        print("===PROCESS===")

        self._process(**kwargs)

        print("")

        return self

    def rm_raw(self, **kwargs):
        self.before_op(**kwargs)
        print("===RM-RAW===")

        self._rm_raw(**kwargs)

        print("")

        return self


    def rm(self, **kwargs):
        self.before_op(**kwargs)

        if os.path.exists(self.path):
            (print)((_coconut.operator.itemgetter(-1))(self.path.split("/")))
            shutil.rmtree(self.path)

        return self

    def rm_subsets(self, **kwargs):
        self.before_op(**kwargs)

        if os.path.exists(self.training_set.path):
            shutil.rmtree(self.training_set.path)

        if os.path.exists(self.test_set.path):
            shutil.rmtree(self.test_set.path)

        return self

    def is_empty(self):
        if not os.path.exists(self.path):
            return True
        else:
            return not os.listdir(self.path)


    @abstractproperty
    def subset_class(self):
        pass

    @abstractproperty
    def help(self):
        pass

    @abstractmethod
    def _download(self):
        pass

    @abstractmethod
    def _extract(self):
        pass


    def _rm_compressed(self, **kwargs):
        pass

    def remove_all_file_with_extension(self, extension):
        for root, dirs, files in os.walk(self.path):
            for file in files:
                file = os.path.join(root, file)
                if file.endswith(".{}".format(extension)):
                    os.remove(file)

    @abstractmethod
    def _process(self):
        pass

    @abstractmethod
    def _rm_raw(self):
        pass

    @abstractmethod
    def reqs(self, **kwargs):
        pass

    @property
    def size(self):
        return self.training_set.size + self.test_set.size

    @property
    def training_set(self):
        if self._training_set is None:
            self._load_dataframe()

        return self._training_set

    @property
    def test_set(self):
        if self._test_set is None:
            self._load_dataframe()

        return self._test_set

    def _build_sets(self, df):
# create mask for distributing train/test set
        df = df.sample(frac=1)

        len_df = len(df)
        msk = np.arange(len_df) < (self.train_prop * len_df)

# select test and training sets
        train = df[msk]
        test = df[~msk]

# set fields
        self._dataframe = df
        self._training_set = self.subset_class(self, train)
        self._test_set = self.subset_class(self, test)
        self._complete_set = self.subset_class(self, df)


class SubSet(object):
    __metaclass__ = ABCMeta

    def __init__(self, dataset, df):
        self.dataset = dataset
        self._dataframe = df

        if df is None:
            raise Exception("None dataframe")


    @property
    def df(self):
        return self._dataframe

    @df.setter
    def df(self, dataframe):
        self._dataframe = dataframe

    @abstractmethod
    def dataframe(self):
        pass

    @abstractmethod
    def arrays(self):
        pass

    @abstractmethod
    def random_batch_dataframe_generator(self, batch_size):
        pass

    @abstractmethod
    def random_batch_arrays_generator(self, batch_size):
        pass

    @property
    def size(self):
        return len(self._dataframe)

    def batch_dataframe_generator(self, batch_size):
        i = 0
        total = self.size

        while i < total:

            _from = i
            _to = min(i + batch_size, total)

            idx = list(range(_from, _to))

            yield self._dataframe.iloc[idx]

            i += batch_size
