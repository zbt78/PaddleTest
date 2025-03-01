# -*- coding: utf-8 -*-
# encoding=utf-8 vi:ts=4:sw=4:expandtab:ft=python
"""
test DarkNet53 model
"""

import os
import sys
import logging
import tarfile
import six
import wget
import pytest
import numpy as np
import paddle.inference as paddle_infer

# pylint: disable=wrong-import-position
sys.path.append("..")
from test_case import InferenceTest


# pylint: enable=wrong-import-position


def check_model_exist():
    """
    check model exist
    """
    DarkNet53_url = "https://paddle-qa.bj.bcebos.com/inference_model_clipped/2.0/class/DarkNet53.tgz"
    if not os.path.exists("./DarkNet53/inference.pdiparams"):
        wget.download(DarkNet53_url, out="./")
        tar = tarfile.open("DarkNet53.tgz")
        tar.extractall()
        tar.close()


def test_config():
    """
    test combined model config
    """
    check_model_exist()
    test_suite = InferenceTest()
    test_suite.load_config(
        model_file="./DarkNet53/inference.pdmodel",
        params_file="./DarkNet53/inference.pdiparams",
    )
    test_suite.config_test()


@pytest.mark.win
@pytest.mark.server
@pytest.mark.trt_fp32
def test_trt_fp32_more_bz():
    """
    compared trt fp32 batch_size=1-2 DarkNet53 outputs with true val
    """
    check_model_exist()

    file_path = "./DarkNet53"
    images_size = 224
    batch_size_pool = [1, 2]
    max_batch_size = 2
    for batch_size in batch_size_pool:
        test_suite = InferenceTest()
        test_suite.load_config(
            model_file="./DarkNet53/inference.pdmodel",
            params_file="./DarkNet53/inference.pdiparams",
        )
        images_list, npy_list = test_suite.get_images_npy(file_path, images_size)
        fake_input = np.array(images_list[0:batch_size]).astype("float32")
        input_data_dict = {"x": fake_input}
        output_data_dict = test_suite.get_truth_val(input_data_dict, device="gpu")

        del test_suite  # destroy class to save memory

        # Cause of the diff error, delete the conv2d_fusion when trt_version < 8.0
        ver = paddle_infer.get_trt_compile_version()
        if ver[0] * 1000 + ver[1] * 100 + ver[2] * 10 < 8000:
            delete_op_list = ["conv2d_fusion"]
        else:
            delete_op_list = []

        test_suite2 = InferenceTest()
        test_suite2.load_config(
            model_file="./DarkNet53/inference.pdmodel",
            params_file="./DarkNet53/inference.pdiparams",
        )
        test_suite2.trt_more_bz_test(
            input_data_dict,
            output_data_dict,
            max_batch_size=max_batch_size,
            min_subgraph_size=1,
            precision="trt_fp32",
            dynamic=True,
            auto_tuned=True,
            delete_op_list=delete_op_list,
        )

        del test_suite2  # destroy class to save memory


@pytest.mark.jetson
@pytest.mark.trt_fp32_more_bz_precision
def test_jetson_trt_fp32_more_bz():
    """
    compared trt fp32 batch_size=1 DarkNet53 outputs with true val
    """
    check_model_exist()

    file_path = "./DarkNet53"
    images_size = 224
    batch_size_pool = [1]
    max_batch_size = 1
    for batch_size in batch_size_pool:
        test_suite = InferenceTest()
        test_suite.load_config(
            model_file="./DarkNet53/inference.pdmodel",
            params_file="./DarkNet53/inference.pdiparams",
        )
        images_list, npy_list = test_suite.get_images_npy(file_path, images_size)
        fake_input = np.array(images_list[0:batch_size]).astype("float32")
        input_data_dict = {"x": fake_input}
        output_data_dict = test_suite.get_truth_val(input_data_dict, device="gpu")

        del test_suite  # destroy class to save memory

        test_suite2 = InferenceTest()
        test_suite2.load_config(
            model_file="./DarkNet53/inference.pdmodel",
            params_file="./DarkNet53/inference.pdiparams",
        )
        test_suite2.trt_more_bz_test(
            input_data_dict,
            output_data_dict,
            max_batch_size=max_batch_size,
            min_subgraph_size=1,
            precision="trt_fp32",
            dynamic=True,
            auto_tuned=True,
        )

        del test_suite2  # destroy class to save memory


@pytest.mark.trt_fp32_multi_thread
def test_trt_fp32_bz1_multi_thread():
    """
    compared trt fp32 batch_size=1 DarkNet53 multi_thread outputs with true val
    """
    check_model_exist()

    file_path = "./DarkNet53"
    images_size = 224
    batch_size = 1
    test_suite = InferenceTest()
    test_suite.load_config(
        model_file="./DarkNet53/inference.pdmodel",
        params_file="./DarkNet53/inference.pdiparams",
    )
    images_list, npy_list = test_suite.get_images_npy(file_path, images_size)
    fake_input = np.array(images_list[0:batch_size]).astype("float32")
    input_data_dict = {"x": fake_input}
    output_data_dict = test_suite.get_truth_val(input_data_dict, device="gpu")

    del test_suite  # destroy class to save memory

    test_suite2 = InferenceTest()
    test_suite2.load_config(
        model_file="./DarkNet53/inference.pdmodel",
        params_file="./DarkNet53/inference.pdiparams",
    )
    test_suite2.trt_bz1_multi_thread_test(
        input_data_dict,
        output_data_dict,
        precision="trt_fp32",
    )

    del test_suite2  # destroy class to save memory
