# project-a

## よく使うコマンド
`pip install -r requirements.txt --ignore-installed`   
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
