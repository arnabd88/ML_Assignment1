
python Assignment1.py -setfold -Attr mush.names -fold 1 datasets/SettingA/training.data -test datasets/SettingA/test.data > Q3_SetA_1


python Assignment1.py -fold 6 datasets/SettingA/CVSplits/training_00.data datasets/SettingA/CVSplits/training_01.data datasets/SettingA/CVSplits/training_02.data datasets/SettingA/CVSplits/training_03.data datasets/SettingA/CVSplits/training_04.data datasets/SettingA/CVSplits/training_05.data -depthOn -Attr mush.names -setfold > Q3_SetA_2


python Assignment1.py -setfold -Attr mush.names -fold 1 datasets/SettingB/training.data -test datasets/SettingB/test.data > Q3_SetB_1

python Assignment1.py -fold 6 datasets/SettingB/CVSplits/training_00.data datasets/SettingB/CVSplits/training_01.data datasets/SettingB/CVSplits/training_02.data datasets/SettingB/CVSplits/training_03.data datasets/SettingB/CVSplits/training_04.data datasets/SettingB/CVSplits/training_05.data -depthOn -Attr mush.names -setfold -test datasets/SettingB/test.data > Q3_SetB_2


