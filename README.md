# project-a

## よく使うコマンド
```
pip install -r requirements.txt --ignore-installed`   
```
```
git reset --soft HEAD^  
git rm --cached *_lst  
```

## Tensorflowのビルド用コマンド
1. configureを実行  
`./configure`  
2. bazelコマンドを使ってtensorflowをコンパイル　  
`bazel build -c opt //tensorflow/tools/pip_package:build_pip_package`　  
3. pip パッケージを作成　  
`bazel-bin/tensorflow/tools/pip_package/build_pip_package /tmp/tensorflow_pkg`　  
4. pip install でインストール　  
`pip install /tmp/tensorflow_pkg/tensorflow-0.9.0-py3-none-any.whl`　 

#### 各サービスのバージョン
|Name|Ver.|
|:---|:---|
|NVIDIA Web Driver|387.10.10.40.105|
|CUDA Driver|396.148|
|CUDA|9.0|
|cuDNN|7.0.4 (Nov 13, 2017), for CUDA 9.0|

## Cuda
- cuda driver   
`/Developer/NVIDIA/`   
⇨driverインストール時にバージョンごとに生成されるので、利用するものをPATHへ追加   
- cuDNN  
`/usr/local/cuda`   
⇨cuDNNをダウンロード後、展開したファイル（lib, include）をこの配下へコピーする必要あり   

## eGPU on mac
- Exec patch to anable eGPU on mac   
https://egpu.io/forums/mac-setup/script-enable-egpu-on-tb1-2-macs-on-macos-10-13-4/

## Conda
- pip installed folder   
`~/miniconda2/envs/[env_name]/lib/python3.6/site-packages/`
