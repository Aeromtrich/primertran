# PyPI 发布流程

本文档记录 PrimerTran 发布到 PyPI 的步骤。发布成功后，用户可以通过 `pip install primertran` 安装。

## 1. 准备 PyPI 账号

注册或登录 PyPI：

```text
https://pypi.org/
```

创建 API Token：

```text
Account settings -> API tokens -> Add API token
```

第一次发布项目时，项目还不存在，Token scope 需要选择：

```text
Entire account
```

发布成功后，可以再创建项目级 token，用于后续版本发布。

## 2. 发布前检查

确认工作区干净：

```bash
git status
```

确认版本号：

```bash
sed -n '1,40p' code/pyproject.toml
```

重点检查：

```toml
name = "primertran"
version = "0.1.0"
```

每次发布新版本前，都需要递增 `version`，例如：

```text
0.1.0 -> 0.1.1
```

## 3. 安装构建工具

建议在项目虚拟环境里执行：

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install build twine
```

## 4. 构建 wheel 和 sdist

PrimerTran 的 Python 包在 `code/` 目录下：

```bash
cd /Volumes/Software/Code/primertran/code
rm -rf dist build *.egg-info
python -m build
```

构建成功后会生成：

```text
dist/primertran-0.1.0-py3-none-any.whl
dist/primertran-0.1.0.tar.gz
```

## 5. 检查发布产物

```bash
python -m twine check dist/*
```

如果输出 `PASSED`，说明包元数据基本可用。

## 6. 上传到 TestPyPI，可选但推荐

TestPyPI 用于预演发布流程：

```bash
python -m twine upload --repository testpypi dist/*
```

用户名输入：

```text
__token__
```

密码输入 TestPyPI API Token。

测试安装：

```bash
python -m pip install --index-url https://test.pypi.org/simple/ primertran
```

## 7. 上传到 PyPI

```bash
python -m twine upload dist/*
```

用户名输入：

```text
__token__
```

密码输入 PyPI API Token。

发布成功后，用户可以安装：

```bash
pip install primertran
```

## 8. 发布 GitHub Release

建议 PyPI 发布和 GitHub Release 使用同一个版本号。

```bash
git tag v0.1.0
git push origin v0.1.0
```

然后在 GitHub 创建 Release：

```text
https://github.com/Aeromtrich/primertran/releases/new
```

## 9. 常见问题

### 版本号已经存在

PyPI 不允许覆盖已发布的同名同版本包。需要修改 `code/pyproject.toml` 里的版本号后重新构建。

### 包名被占用

如果 `primertran` 在 PyPI 上已经被别人占用，需要更换 `project.name`。

### README 显示不完整

PyPI 使用 `code/pyproject.toml` 中的：

```toml
readme = "README.md"
```

因为构建目录是 `code/`，这里指的是 `code/README.md`。

### 不要提交 dist 目录

`dist/` 是构建产物，通常不需要提交到 git。
