# SPDX-FileCopyrightText: Copyright (c) 2021 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Copyright (c) 2021 ETH Zurich, Nikita Rudin

import glob

from legged_gym.envs.base.legged_robot_config import LeggedRobotCfg, LeggedRobotCfgPPO

MOTION_FILES = glob.glob("datasets/pikachu/pikachu_walk/*")
# MOTION_FILES = [
#     # "datasets/bdx/placo_moves/bdx_walk_forward.txt", # OK
#     "datasets/bdx/placo_moves_trunk_pitch/bdx_walk_forward.txt",
#     # "datasets/bdx/placo_moves_higher/bdx_walk_forward.txt",
# ]

NO_FEET = False  # Do not use feet in the amp observations and data


class PikachuAMPCfg(LeggedRobotCfg):
    class env(LeggedRobotCfg.env):
        num_envs = 4096

        # num_observations   = num_privileged_obs - 6 (Remove velocity observations from policy observation.)
        # num_privileged_obs = 3 + 3 + 3 + 3 + num_dof + num_dof + num_actions
        num_observations = 36
        num_privileged_obs = 42
        num_actions = 10
        env_spacing = 2.0
        reference_state_initialization = False
        reference_state_initialization_prob = 0.85
        amp_motion_files = MOTION_FILES
        ee_names = ["left_foot", "right_foot"]
        get_commands_from_joystick = False
        get_commands_from_keyboard = False
        episode_length_s = 8  # episode length in seconds
        debug_save_obs = False
        no_feet = NO_FEET

        # RMA
        # If num_rma_obs = 0, RMA is not used
        # num_rma_obs = 0
        num_rma_obs = 16

        include_history_steps = None if num_rma_obs == 0 else 15

    class init_state(LeggedRobotCfg.init_state):
        pos = [0.0, 0.0, 0.15]  # x,y,z [m]
        # pos = [0.0, 0.0, 0.3]  # x,y,z [m]
        rot = [0, 0, 0, 1]

        default_joint_angles = {
           'left_hip_yaw_joint' : 0. ,   
           'left_hip_roll_joint' : 0,               
           'left_hip_pitch_joint' : 0.3,         
           'left_knee_joint' : 1.12,       
           'left_ankle_joint' : 0.8,     
           'right_hip_yaw_joint' : 0., 
           'right_hip_roll_joint' : 0, 
           'right_hip_pitch_joint' : 0.3,                                       
           'right_knee_joint' : 1.12,                                             
           'right_ankle_joint' : 0.8,        
        }

    class control(LeggedRobotCfg.control):
        # PD Drive parameters:
        control_type = "P"
        # override_effort = False
        # # effort = 0.93  # Nm
        # # effort = 0.52  # Nm


        stiffness = {'hip_pitch': 80,
                     'hip_roll': 50,
                     'hip_yaw': 25,
                     'knee': 50,
                     'ankle': 50,
                     }  # [N*m/rad]
        
        damping = {  'hip_pitch': 1,
                     'hip_roll': 0.6,
                     'hip_yaw': 0.05,
                     'knee': 0.1,
                     'ankle': 0.01,
                     }  # [N*m/rad]  # [N*m*s/rad]

        # action scale: target angle = actionScale * action + defaultAngle
        action_scale = 0.25  # 0.25
        # action_scale = 1.0  # 0.25

        # decimation: Number of control action updates @ sim DT per policy DT
        # decimation = 2  # 120hz control if dt 240hz, 60hz if dt 120hz
        decimation = 4  # 30hz control if dt 120hz, 60hz if dt 240hz

        action_filter = False
        cutoff_frequency = 10

    class terrain(LeggedRobotCfg.terrain):
        mesh_type = "plane"  # "heightfield" # none, plane, heightfield or trimesh
        # terrain types: [smooth slope, rough slope, stairs up, stairs down, discrete]
        terrain_proportions = [0, 1.0, 0, 0, 0.0]
        # trimesh only:
        # slope_treshold = (
        #     0.75  # slopes above this threshold will be corrected to vertical surfaces
        # )
        # vertical_scale = 0.001  # [m]

        # mesh_type = "plane"
        measure_heights = False
        static_friction = 5.0  # 5
        dynamic_friction = 5.0  # 5

    class asset(LeggedRobotCfg.asset):
        # file = "{LEGGED_GYM_ROOT_DIR}/resources/robots/Pikachu_V025/urdf/Pikachu_V025_flat.urdf"
        file = "{LEGGED_GYM_ROOT_DIR}/resources/robots/Pikachu_V025/urdf/Pikachu_V025.urdf"
        # foot_name = "foot"
        # end link
        foot_name = "ankle"
        penalize_contacts_on = []
        terminate_after_contacts_on = [
        "base_link"
        ]
        flip_visual_attachments = False
        self_collisions = 1  # 1 to disable, 0 to enable...bitwise filter
        # default_dof_drive_mode = 0  # see GymDofDriveModeFlags (0 is none, 1 is pos tgt, 2 is vel tgt, 3 effort)
        disable_gravity = False
        fix_base_link = False  # fix the base of the robot

        angular_damping = 0.0  # 0.01
        thickness = 0.01 # 0.001
        damping = 0.1
        armature = 0.0018
        friction = 0.058

    class sim(LeggedRobotCfg.sim):
        dt = 0.005  # 120hz
        # dt = 0.00416665  # 240hz
        substeps = 1

    class domain_rand:
        randomize_friction = True
        friction_range = [0.95, 1.05]
        randomize_base_mass = True
        added_mass_range = [-0.01, 0.01]
        push_robots = False
        push_interval_s = 3
        max_push_vel_xy = 0.5  # 0.3
        randomize_gains = False
        stiffness_multiplier_range = [0.99, 1.01]
        damping_multiplier_range = [0.99, 1.01]
        randomize_torques = True
        torque_multiplier_range = [0.95, 1.05]
        randomize_com = True # 随机质心
        com_range = [-0.01, 0.01]
        observation_lag = True
        observation_lag_range = [0, 1]  # ms

    class noise:
        add_noise = True
        noise_level = 1.0  # scales other values

        class noise_scales:
            dof_pos = 0.01
            dof_vel = 0.01  # finish with very large dof_vel ? 1.5
            lin_vel = 0.01
            ang_vel = 0.01
            gravity = 0.01
            height_measurements = 0.1

    class rewards(LeggedRobotCfg.rewards):
        soft_dof_pos_limit = 0.9
        base_height_target = 0.15
        tracking_sigma = 0.1  # tracking reward = exp(-error^2/sigma)

        class scales(LeggedRobotCfg.rewards.scales):
            termination = 0.0
            tracking_lin_vel = 2 * 1.0 / (0.004 * 4)
            tracking_ang_vel = 1 * 1.0 / (0.004 * 4)
            # tracking_lin_vel = 1.0
            # tracking_ang_vel = 0.5
            lin_vel_z = 0.0
            ang_vel_xy = 0.0
            orientation = 0.0
            torques = -0.000025  # -0.000025
            dof_vel = 0.0
            dof_acc = 0.0
            base_height = -1.0  # -1.0
            feet_air_time = 0.0
            collision = 0.0
            feet_stumble = 0.0
            action_rate = -1.0  # -1.0
            stand_still = 0.0
            dof_pos_limits = 0.0
            action_smoothness = -0.002
            feet_air_time= 0.1
            stumble = -0.01

    class commands:
        curriculum = False  # False
        max_curriculum = 0.2
        num_commands = 4  # default: lin_vel_x, lin_vel_y, ang_vel_yaw, heading (in heading mode ang_vel_yaw is recomputed from heading error)
        resampling_time = 10.0  # time before command are changed[s]
        heading_command = False  # if true: compute ang vel command from heading error

        class ranges:
            lin_vel_x =   [-0.185, 0.185]  # min max [m/s] # 0.14 ok
            lin_vel_y =   [-0.185, 0.185]  # min max [m/s] # 0.1 ok
            ang_vel_yaw = [-0.185, 0.185]  # min max [rad/s] # 0.3 ok
            heading = [0, 0]

    class viewer(LeggedRobotCfg.viewer):
        ref_env = 0
        pos = [0, 0, 1]  # [m]
        lookat = [11.0, 5, 1.0]  # [m]


class PikachuAMPCfgPPO(LeggedRobotCfgPPO):
    runner_class_name = "AMPOnPolicyRunner"

    class policy:
        init_noise_std = 0.8 # 0.8
        actor_hidden_dims = [512, 256, 128]
        critic_hidden_dims = [512, 256, 128]
        activation = "elu"  # can be elu, relu, selu, crelu, lrelu, tanh, sigmoid
        # only for 'ActorCriticRecurrent':
        # rnn_type = 'lstm'
        # rnn_hidden_size = 512
        # rnn_num_layers = 1

    class algorithm(LeggedRobotCfgPPO.algorithm):
        entropy_coef = 0.01
        amp_replay_buffer_size = 1000000
        num_learning_epochs = 5
        num_mini_batches = 4
        disc_coef = 5  # 5
        # bounds_loss_coef = 10  # commented

    class runner(LeggedRobotCfgPPO.runner):
        run_name = ""
        experiment_name = "pikachu_amp"
        algorithm_class_name = "AMPPPO"
        policy_class_name = "ActorCritic"
        max_iterations = 50000  # number of policy updates
        save_interval = 100  # check for potential saves every this many iterations

        no_feet = NO_FEET

        amp_reward_coef = 2.0  # 2.0
        amp_motion_files = MOTION_FILES
        amp_num_preload_transitions = 2000000
        amp_task_reward_lerp = 0.3  # 0.3 0.1
        amp_discr_hidden_dims = [1024, 512]

        # 判别器梯度惩罚系数
        disc_grad_penalty = 5  # original 10 , bdx 5

        # Large incentivizes exploration
        # min_normalized_std = [0.02] * 15  # 0.02

        min_normalized_std = [0.02] * 10  # 0.02
        # min_normalized_std = None
