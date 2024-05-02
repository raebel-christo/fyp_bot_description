from ament_index_python.packages import get_package_share_directory
from pathlib import Path
from launch import LaunchDescription
from launch_ros.actions import LifecycleNode
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, Command, PythonExpression
from launch.actions import LogInfo
from launch.conditions import IfCondition, UnlessCondition
from nav2_common.launch import HasNodeParams

import lifecycle_msgs.msg
import os


def generate_launch_description():
    description_dir = get_package_share_directory('fyp_bot_description')
    parameter_file = LaunchConfiguration('params_file')
    rviz_config_path = os.path.join(description_dir, 'rviz/urdf_config.rviz')
    default_model_path_1 = os.path.join(description_dir, 'src/description/fyp_bot1_description.urdf')
    default_model_path_2 = os.path.join(description_dir, 'src/description/fyp_bot2_description.urdf')
    slam_path = os.path.join(get_package_share_directory("slam_toolbox"),
        'config',
        'mapper_params_online_sync.yaml')
    use_sim_time = LaunchConfiguration('use_sim_time')
    slam_params_file = LaunchConfiguration('slam_params_file')


    declare_use_sim_time_argument = DeclareLaunchArgument(
        'use_sim_time',
        default_value='false',
        description='Use simulation/Gazebo clock')
    declare_params_file_cmd = DeclareLaunchArgument(
        'slam_params_file',
        default_value=slam_path,
        description='Full path to the ROS2 parameters file to use for the slam_toolbox node')
    has_node_params = HasNodeParams(source_file=slam_params_file,
                                    node_name='slam_toolbox')

    actual_params_file = PythonExpression(['"', slam_params_file, '" if ', has_node_params,
                                           ' else "', slam_path, '"'])

    robot_state_publisher_node = Node(
        namespace='bot1',
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', LaunchConfiguration('model1')])}]
    )
    joint_state_publisher_node = Node(
        namespace='bot1',
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        arguments=[default_model_path_1],
        condition=UnlessCondition(LaunchConfiguration('gui'))
    )
    robot_state_publisher_node_2 = Node(
        namespace='bot2',
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': Command(['xacro ', LaunchConfiguration('model2')])}]
    )
    joint_state_publisher_node_2 = Node(
        namespace='bot2',
        package='joint_state_publisher',
        executable='joint_state_publisher',
        name='joint_state_publisher',
        arguments=[default_model_path_2],
        condition=UnlessCondition(LaunchConfiguration('gui'))
    )
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=['-d', LaunchConfiguration('rvizconfig')],
    )
    rf2o_odometry_node_2 = Node(
        namespace='bot2',
    	package='rf2o_laser_odometry',
    	executable='rf2o_laser_odometry_node',
    	name='laser_odometry',
    	output='screen',
    	parameters=[{
                'laser_scan_topic' : '/bot2/scan',
                'odom_topic' : '/bot2/odom_rf2o',
                'publish_tf' : True,
                'base_frame_id' : '/bot2/base_link',
                'odom_frame_id' : '/bot2/odom',
                'init_pose_from_topic' : '',
                'freq' : 20.0}],
    )
    rf2o_odometry_node = Node(
        namespace='bot1',
    	package='rf2o_laser_odometry',
    	executable='rf2o_laser_odometry_node',
    	name='laser_odometry',
    	output='screen',
    	parameters=[{
                'laser_scan_topic' : '/bot1/scan',
                'odom_topic' : '/bot1/odom_rf2o',
                'publish_tf' : True,
                'base_frame_id' : '/bot1/base_link',
                'odom_frame_id' : '/bot1/odom',
                'init_pose_from_topic' : '',
                'freq' : 20.0}],
    )
    slam = Node(
        parameters=[
          actual_params_file,
          {'use_sim_time': use_sim_time}
        ],
        package='slam_toolbox',
        executable='sync_slam_toolbox_node',
        name='slam_toolbox',
        output='screen')

    return LaunchDescription([
        declare_use_sim_time_argument,
        declare_params_file_cmd,
        DeclareLaunchArgument(name='gui', default_value='True'),
        DeclareLaunchArgument(name='model1', default_value=default_model_path_1),
        DeclareLaunchArgument(name='model2', default_value=default_model_path_2),
        DeclareLaunchArgument(name='rvizconfig', default_value=rviz_config_path),
        DeclareLaunchArgument(name='use_sim_time', default_value='false'),
        robot_state_publisher_node,
        joint_state_publisher_node,
        robot_state_publisher_node_2,
        joint_state_publisher_node_2,
        rviz_node,
        rf2o_odometry_node,
        rf2o_odometry_node_2,
        #slam,
    ])
