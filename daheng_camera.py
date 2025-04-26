import sys
import logging
from gxipy.gxiapi import *
from gxipy.gxidef import *
import ctypes
import numpy as np
from os import getcwd
from PIL import Image
import time

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='camera_operation.log'
)


# 枚举设备
def enum_devices(device=0, device_way=False):
    """
    device = 0  枚举网口、USB口、未知设备、cameralink 设备
    device = 1 枚举GenTL设备
    """
    logging.info("枚举设备")
    try:
        device_manager = DeviceManager()
        dev_num, dev_info_list = device_manager.update_device_list()
        if dev_num == 0:
            logging.error("find no device!")
            print("find no device!")
            sys.exit()
        logging.info(f"Find {dev_num} devices!")
        print("Find %d devices!" % dev_num)
        return dev_info_list
    except Exception as e:
        logging.error(f"Error enumerating devices: {e}")
        print(f"Error enumerating devices: {e}")
        sys.exit()


# 判断不同类型设备
def identify_different_devices(dev_info_list):
    logging.info("判断不同类型设备")
    try:
        # 判断不同类型设备，并输出相关信息
        for i in range(len(dev_info_list)):
            dev_info = dev_info_list[i]
            if dev_info['interface_type'] == GX_INTERFACE_TYPE_ETHERNET:
                logging.info(f"\n网口设备序号: [{i}]")
                print("\n网口设备序号: [%d]" % i)
                logging.info(f"当前设备型号名: {dev_info['model_name']}")
                print("当前设备型号名: %s" % dev_info['model_name'])
                logging.info(f"当前 ip 地址: {dev_info['ip_address']}")
                print("当前 ip 地址: %s" % dev_info['ip_address'])
            elif dev_info['interface_type'] == GX_INTERFACE_TYPE_USB:
                logging.info(f"\nU3V 设备序号: [{i}]")
                print("\nU3V 设备序号: [%d]" % i)
                logging.info(f"当前设备型号名 : {dev_info['model_name']}")
                print("当前设备型号名 : %s" % dev_info['model_name'])
                logging.info(f"当前设备序列号 : {dev_info['serial_number']}")
                print("当前设备序列号 : %s" % dev_info['serial_number'])
            elif dev_info['interface_type'] == GX_INTERFACE_TYPE_1394:
                logging.info(f"\n1394-a/b device: [{i}]")
                print("\n1394-a/b device: [%d]" % i)
            elif dev_info['interface_type'] == GX_INTERFACE_TYPE_CAMERALINK:
                logging.info(f"\ncameralink device: [{i}]")
                print("\ncameralink device: [%d]" % i)
                logging.info(f"当前设备型号名 : {dev_info['model_name']}")
                print("当前设备型号名 : %s" % dev_info['model_name'])
                logging.info(f"当前设备序列号 : {dev_info['serial_number']}")
                print("当前设备序列号 : %s" % dev_info['serial_number'])
    except Exception as e:
        logging.error(f"Error identifying device types: {e}")
        print(f"Error identifying device types: {e}")


# 输入需要连接的相机的序号
def input_num_camera(dev_info_list):
    logging.info("输入需要连接的相机的序号")
    while True:
        try:
            nConnectionNum = int(input("please input the number of the device to connect:"))
            if nConnectionNum < len(dev_info_list):
                return nConnectionNum
            else:
                logging.warning("input error! Please try again.")
                print("input error! Please try again.")
        except ValueError:
            logging.warning("Invalid input! Please enter a valid integer.")
            print("Invalid input! Please enter a valid integer.")


# 创建相机实例并创建句柄,(设置日志路径)
def creat_camera(dev_info_list, nConnectionNum, log=True, log_path=getcwd()):
    """
    :param dev_info_list:     设备列表
    :param nConnectionNum:    需要连接的设备序号
    :param log:               是否创建日志
    :param log_path:          日志保存路径
    :return:                  相机实例
    """
    logging.info("创建相机实例并创建句柄,(设置日志路径)")
    try:
        device_manager = DeviceManager()
        cam = device_manager.open_device_by_index(nConnectionNum + 1)
        logging.info("Camera instance created successfully.")
        return cam
    except Exception as e:
        logging.error(f"Error creating camera instance: {e}")
        print(f"Error creating camera instance: {e}")
        sys.exit()


# 获取各种类型节点参数
def get_Value(device, param_type="int_value", node_name="PayloadSize"):
    """
    获取大恒相机参数的通用函数

    :param device: 相机实例
    :param param_type: 参数类型，支持以下类型：
        - "int_value": 整数类型
        - "float_value": 浮点数类型
        - "enum_value": 枚举类型
        - "bool_value": 布尔类型
        - "string_value": 字符串类型
    :param node_name: 参数名称
    :return: 获取到的参数值
    """
    logging.info("获取各种类型节点参数")
    if param_type == "int_value":
        # 获取整数类型参数
        if hasattr(device, node_name):
            feature = getattr(device, node_name)
            if isinstance(feature, IntFeature):
                value = feature.get()
                print(f"获取 {node_name} 成功！值为 {value}")
                return value
            else:
                print(f"{node_name} 不是整数类型参数！")
                return None
        else:
            print(f"设备不支持 {node_name} 参数！")
            return None

    elif param_type == "float_value":
        # 获取浮点数类型参数
        if hasattr(device, node_name):
            feature = getattr(device, node_name)
            if isinstance(feature, FloatFeature):
                value = feature.get()
                print(f"获取 {node_name} 成功！值为 {value}")
                return value
            else:
                print(f"{node_name} 不是浮点数类型参数！")
                return None
        else:
            print(f"设备不支持 {node_name} 参数！")
            return None

    elif param_type == "enum_value":
        # 获取枚举类型参数
        if hasattr(device, node_name):
            feature = getattr(device, node_name)
            if isinstance(feature, EnumFeature):
                value = feature.get()[0]  # 获取枚举值
                print(f"获取 {node_name} 成功！值为 {value}")
                return value
            else:
                print(f"{node_name} 不是枚举类型参数！")
                return None
        else:
            print(f"设备不支持 {node_name} 参数！")
            return None

    elif param_type == "bool_value":
        # 获取布尔类型参数
        if hasattr(device, node_name):
            feature = getattr(device, node_name)
            if isinstance(feature, BoolFeature):
                value = feature.get()
                print(f"获取 {node_name} 成功！值为 {value}")
                return value
            else:
                print(f"{node_name} 不是布尔类型参数！")
                return None
        else:
            print(f"设备不支持 {node_name} 参数！")
            return None

    elif param_type == "string_value":
        # 获取字符串类型参数
        if hasattr(device, node_name):
            feature = getattr(device, node_name)
            if isinstance(feature, StringFeature):
                value = feature.get()
                print(f"获取 {node_name} 成功！值为 {value}")
                return value
            else:
                print(f"{node_name} 不是字符串类型参数！")
                return None
        else:
            print(f"设备不支持 {node_name} 参数！")
            return None

    else:
        print(f"不支持的参数类型: {param_type}")
        return None


# 设置各种类型节点参数
def set_Value(cam, node_name = None, param_type = 'int_value', node_value = None):
    """
    设置大恒相机参数的通用函数

    :param device: 相机实例
    :param param_type: 参数类型，支持以下类型：
        - "int": 整数类型
        - "float": 浮点数类型
        - "enum": 枚举类型
        - "bool": 布尔类型
        - "string": 字符串类型
    :param node_name: 参数名称
    :param node_value: 要设置的值
    :return: None
    """
    logging.info("设置各种类型节点参数")
    if param_type == "int_value":
        # 设置整数类型参数
        if hasattr(cam, node_name):
            feature = getattr(cam, node_name)
            if isinstance(feature, IntFeature):
                feature.set(node_value)
                print(f"设置 {node_name} 为 {node_value} 成功！")
            else:
                print(f"{node_name} 不是整数类型参数！")
        else:
            print(f"设备不支持 {node_name} 参数！")

    elif param_type == "float_value":
        # 设置浮点数类型参数
        if hasattr(cam, node_name):
            feature = getattr(cam, node_name)
            if isinstance(feature, FloatFeature):
                feature.set(node_value)
                print(f"设置 {node_name} 为 {node_value} 成功！")
            else:
                print(f"{node_name} 不是浮点数类型参数！")
        else:
            print(f"设备不支持 {node_name} 参数！")

    elif param_type == "enum_value":
        # 设置枚举类型参数
        if hasattr(cam, node_name):
            feature = getattr(cam, node_name)
            if isinstance(feature, EnumFeature):
                feature.set(node_value)
                print(f"设置 {node_name} 为 {node_value} 成功！")
            else:
                print(f"{node_name} 不是枚举类型参数！")
        else:
            print(f"设备不支持 {node_name} 参数！")

    elif param_type == "bool_value":
        # 设置布尔类型参数
        if hasattr(cam, node_name):
            feature = getattr(cam, node_name)
            if isinstance(feature, BoolFeature):
                feature.set(node_value)
                print(f"设置 {node_name} 为 {node_value} 成功！")
            else:
                print(f"{node_name} 不是布尔类型参数！")
        else:
            print(f"设备不支持 {node_name} 参数！")

    elif param_type == "string_value":
        # 设置字符串类型参数
        if hasattr(cam, node_name):
            feature = getattr(cam, node_name)
            if isinstance(feature, StringFeature):
                feature.set(node_value)
                print(f"设置 {node_name} 为 {node_value} 成功！")
            else:
                print(f"{node_name} 不是字符串类型参数！")
        else:
            print(f"设备不支持 {node_name} 参数！")

    else:
        print(f"不支持的参数类型: {param_type}")



# 判断相机是否处于连接状态(返回值如何获取)
def decide_divice_on_line(cam):
    logging.info("判断相机是否处于连接状态(返回值如何获取)")
    try:
        is_connected = cam.is_open()
        if is_connected:
            logging.info("该设备在线 ！")
            print("该设备在线 ！")
        else:
            logging.warning(f"该设备已掉线 ！{is_connected}")
            print("该设备已掉线 ！", is_connected)
    except Exception as e:
        logging.error(f"Error checking device connection: {e}")
        print(f"Error checking device connection: {e}")


# 主动图像采集
def access_get_image(cam, active_way="getImagebuffer"):
    """
    :param cam:     相机实例
    :active_way:主动取流方式的不同方法 分别是（getImagebuffer）（getoneframetimeout）
    :return:
    """
    logging.info("主动图像采集")
    try:
        if active_way == "getImagebuffer":
            while True:
                try:
                    raw_image = cam.data_stream[0].get_image()
                    if raw_image is not None:
                        numpy_image = raw_image.get_numpy_array()
                        if len(numpy_image.shape) == 2:  # 单通道图像
                            numpy_image = np.dstack((numpy_image, numpy_image, numpy_image))  # 转换为三通道
                        elif len(numpy_image.shape) == 3:
                            numpy_image = np.transpose(numpy_image, (2, 0, 1))
                        logging.info("Got an image")
                        print("Got an image")
                    else:
                        logging.warning("no data")
                        print("no data")
                except Exception as e:
                    logging.error(f"Error getting image: {e}")
                    print(f"Error getting image: {e}")
        elif active_way == "getoneframetimeout":
            while True:
                try:
                    raw_image = cam.data_stream[0].get_image()
                    if raw_image is not None:
                        numpy_image = raw_image.get_numpy_array()
                        if len(numpy_image.shape) == 2:  # 单通道图像
                            numpy_image = np.dstack((numpy_image, numpy_image, numpy_image))  # 转换为三通道
                        elif len(numpy_image.shape) == 3:
                            numpy_image = np.transpose(numpy_image, (2, 0, 1))
                        logging.info("Got an image")
                        print("Got an image")
                    else:
                        logging.warning("no data")
                        print("no data")
                except Exception as e:
                    logging.error(f"Error getting image: {e}")
                    print(f"Error getting image: {e}")
    except KeyboardInterrupt:
        logging.info("Image acquisition stopped by user.")
        print("Image acquisition stopped by user.")


# 回调取图采集
def capture_callback_color(raw_image):
    logging.info("回调取图采集")
    try:
        # print height, width, and frame ID of the acquisition image
        logging.info(f"Frame ID: {raw_image.get_frame_id()}   Height: {raw_image.get_height()}   Width: {raw_image.get_width()}")
        print("Frame ID: %d   Height: %d   Width: %d"
              % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width()))

        # get RGB image from raw image
        rgb_image = raw_image.convert("RGB")
        if rgb_image is None:
            logging.error('Failed to convert RawImage to RGBImage')
            print('Failed to convert RawImage to RGBImage')
            return

        # create numpy array with data from rgb image
        numpy_image = rgb_image.get_numpy_array()
        if numpy_image is None:
            logging.error('Failed to get numpy array from RGBImage')
            print('Failed to get numpy array from RGBImage')
            return

        if len(numpy_image.shape) == 3:
            numpy_image = np.transpose(numpy_image, (2, 0, 1))
        # show acquired image
        img = Image.fromarray(numpy_image, 'RGB')
        img.show()
    except Exception as e:
        logging.error(f"Error in color callback: {e}")
        print(f"Error in color callback: {e}")


def capture_callback_mono(raw_image):
    logging.info("capture_callback_mono")
    try:
        # print height, width, and frame ID of the acquisition image
        logging.info(f"Frame ID: {raw_image.get_frame_id()}   Height: {raw_image.get_height()}   Width: {raw_image.get_width()}")
        print("Frame ID: %d   Height: %d   Width: %d"
              % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width()))

        # create numpy array with data from raw image
        numpy_image = raw_image.get_numpy_array()
        if numpy_image is None:
            logging.error('Failed to get numpy array from RawImage')
            print('Failed to get numpy array from RawImage')
            return

        if len(numpy_image.shape) == 2:  # 单通道图像
            numpy_image = np.dstack((numpy_image, numpy_image, numpy_image))  # 转换为三通道
        elif len(numpy_image.shape) == 3:
            numpy_image = np.transpose(numpy_image, (2, 0, 1))
        # show acquired image
        img = Image.fromarray(numpy_image, 'RGB')  # 改为 'RGB' 模式显示
        img.show()
    except Exception as e:
        logging.error(f"Error in mono callback: {e}")
        print(f"Error in mono callback: {e}")


# 注册回调取图
def call_back_get_image(cam):
    logging.info("注册回调取图")
    try:
        data_stream = cam.data_stream[0]
        if cam.PixelColorFilter.is_implemented() is True:
            data_stream.register_capture_callback(capture_callback_color)
        else:
            data_stream.register_capture_callback(capture_callback_mono)
        logging.info("Callback registered successfully.")
        return data_stream
    except Exception as e:
        logging.error(f"Error registering callback: {e}")
        print(f"Error registering callback: {e}")
        return None


# 关闭设备与销毁句柄
def close_and_destroy_device(cam, data_stream=None):
    logging.info("关闭设备与销毁句柄")
    try:
        if data_stream:
            data_stream.unregister_capture_callback()
        cam.close()
        logging.info("Device closed successfully.")
    except Exception as e:
        logging.error(f"Error closing device: {e}")
        print(f"Error closing device: {e}")


# 开启取流并获取数据包大小
def start_grab_and_get_data_size(cam):
    logging.info("开启取流并获取数据包大小")
    try:
        cam.stream_on()
        logging.info("Image streaming started.")
    except Exception as e:
        logging.error(f"Error starting image streaming: {e}")
        print(f"Error starting image streaming: {e}")


def main():
    cam = None
    data_stream = None
    try:
        # 获得设备信息
        dev_info_list = enum_devices()

        # 判断不同类型设备
        identify_different_devices(dev_info_list)

        # 选择设备
        nConnectionNum = input_num_camera(dev_info_list)

        # 创建相机实例
        cam = creat_camera(dev_info_list, nConnectionNum)

        # 打印相机支持的所有节点名称
        print_all_nodes(cam)
        # 设置设备的一些参数
        set_Value(cam, param_type="float_value", node_name="ExposureTime", node_value=15000)
        set_Value(cam, param_type="float_value", node_name="Gain", node_value=12)

        if dev_info_list[nConnectionNum].get("device_class") == GxDeviceClassList.USB2:
            # set trigger mode
            cam.TriggerMode.set(GxSwitchEntry.ON)
        else:
            # set trigger mode and trigger source
            cam.TriggerMode.set(GxSwitchEntry.ON)
            cam.TriggerSource.set(GxTriggerSourceEntry.SOFTWARE)

        stdcall = input("回调方式取流显示请输入 0    主动取流方式显示请输入 1:")
        if stdcall == '0':
            # 注册回调取图
            data_stream = call_back_get_image(cam)

            # 开启设备取流
            start_grab_and_get_data_size(cam)

            logging.info('<Start acquisition>')
            print('<Start acquisition>')
            time.sleep(0.1)

            # Send trigger command
            cam.TriggerSoftware.send_command()
            logging.info("Software trigger command sent.")

            # Waiting callback
            time.sleep(1)

            # stop acquisition
            cam.stream_off()
            logging.info('<Stop acquisition>')
            print('<Stop acquisition>')

            # 关闭设备与销毁句柄
            close_and_destroy_device(cam, data_stream)
        elif stdcall == '1':
            # 开启设备取流
            start_grab_and_get_data_size(cam)
            # 主动取流方式抓取图像
            access_get_image(cam, active_way="getImagebuffer")
            # 关闭设备与销毁句柄
            close_and_destroy_device(cam)
        else:
            logging.warning("Invalid input!")
            print("Invalid input!")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
    finally:
        if cam:
            close_and_destroy_device(cam, data_stream)


if __name__ == "__main__":
    main()