# D环境与POC验证操作手册

## D的职责和最终成果

D负责让源代码与靶场真实运行的程序一致，提供所有成员可复用的验证环境和POC记录规范。D构造并初审S017—S024，负责S010、S011、S022的9条正式观察，复核A的记录；D的记录由C复核。D还完成一例SQLi及一例XSS的Burp联动演示。

以下步骤以Windows上Docker Desktop和WSL Ubuntu为例。先在一台电脑验证，第二台按同一提交和配置复现。不要把含漏洞的DVWA暴露到公网。操作里标明了“可能受上游版本影响”的地方，现场应以官方仓库的实际文件为准。

## 一  环境搭建从检查开始

打开Docker Desktop并确认WSL集成已开启。进入WSL终端验证版本：

```bash
docker version
docker compose version
git --version
php --version
```

宿主机没有php命令不影响运行Docker方案；PHP语法检查可在DVWA容器里做。如果docker version出现连接失败，先确认Docker Desktop运行和本发行版WSL集成，而非重新克隆源码。

在操作包的根目录建立third_party，获取官方DVWA：

```bash
cd ~/llm-web-lab
mkdir -p third_party
cd third_party
git clone https://github.com/digininja/DVWA.git
cd DVWA
git rev-parse HEAD
docker compose up -d
docker compose ps
```

在浏览器打开http://127.0.0.1:4280。按页面提示访问Setup DVWA，点击Create / Reset Database，然后登录并选择所需安全级别。官方README记载默认登录为admin/password，但启动前仍以所用版本的说明和实际页面为准。容器compose在仓库版本中将DVWA映射到127.0.0.1:4280；若端口变了，先核对实际compose配置。

保存docker compose config、docker compose ps、git rev-parse HEAD、镜像ID、数据库与浏览器版本到environment/version.txt。版本固定时可将上游仓库锁到所记录的提交；必要时将镜像固定到实际摘要，不再依赖latest的漂移。

```bash
docker compose config > ../../environment/compose_effective.txt
docker compose ps > ../../environment/services.txt
git rev-parse HEAD > ../../environment/dvwa_commit.txt
docker image inspect ghcr.io/digininja/dvwa:latest --format '{{.Id}}' \
  > ../../environment/dvwa_image_id.txt
```

上述输出路径假定终端位于third_party/DVWA。若Docker镜像命名被本地配置修改，应从docker compose config查看实际镜像名。服务未就绪时查docker compose logs --tail=100，不要把错误栈改写成“部署成功”。

## 二  确保“审计源码＝实际运行源码”

初始compose使用预构建镜像，编辑本地PHP源码不一定改变服务。若要验证本组派生案例，建议遵循官方本地源码挂载说明：在compose.yml中启用应用源码的bind mount，并按官方README从config/config.inc.php.dist复制出config/config.inc.php；然后重建或重启服务。

```bash
cd ~/llm-web-lab/third_party/DVWA
cp config/config.inc.php.dist config/config.inc.php
```

在compose.yml中启用官方注释给出的`./:/var/www/html`挂载。修改配置前保存原始compose.yml到environment或提交自己的实验分支。再次执行docker compose up -d，先访问普通页面，再检查本地与容器内一个目标PHP文件是否一致。

```bash
sha256sum vulnerabilities/sqli/source/low.php
docker compose exec -T dvwa sha256sum \
  /var/www/html/vulnerabilities/sqli/source/low.php
```

两端哈希不同就停止对该文件进行“源码与POC”结论配对。新建的教学案例位于独立lab_cases目录，C与D商定实际URL，并对它们做相同的哈希检查。若新版官方镜像中的目录变化，先用容器内pwd与ls确认，不要靠猜测。镜像拉取失败可以使用官方本地构建方式，但记录构建提交和镜像ID后全组保持同一环境。

## 三  教学数据与样本运行

D准备一个小型lab_people表和若干虚构用户，仅供SQLi案例；C按样本卡组织查询与页面，D提供公共数据库连接与可运行外壳。表名、字符集和行数固定，供普通请求及条件改变对照。真实姓名和真实凭据不进入教学数据。

```sql
CREATE TABLE IF NOT EXISTS lab_people (
  id INT PRIMARY KEY,
  name VARCHAR(80) NOT NULL
) CHARACTER SET utf8mb4;
INSERT INTO lab_people(id,name) VALUES (1,'Alice'),(2,'Bob'),(3,'Carol');
```

上述SQL首次建表使用；第二次运行INSERT可能因主键重复失败，这正是应记录并处理的状态。可在初始化说明里改为先清空教学表再插入，但只针对lab_people，不能用`docker compose down -v`作为随意的日常重置，它会清掉包含DVWA初始化数据的卷。

测试XSS存储案例前清理该案例自己的留言数据，记录执行人、时间和表名。反射型样本每次普通业务测试从干净URL开始。每条样本由C的sample_card说明启动URL、参数、会话状态、预期业务与重置方式，D确认在容器中可运行。

### PHP语法检查

```bash
docker compose exec -T dvwa php -l \
  /var/www/html/lab_cases/S001/index.php
```

语法检查通过仅说明PHP可解析，不能替代HTTP访问、数据库查询或浏览器脚本验证。

## 四  先建立人工参考验证

从目标案例保存正常请求与响应，再构造受控异常输入，观察差异。SQLi示例可让模型设计不改数据的真假条件，人工检查普通返回、错误返回、结果集变化或请求日志。不要只凭SQL错误页推断能够读出敏感信息。

XSS使用不会读取Cookie或向外发送数据的页面标记。下面的文本仅用于本机教学验证；实际触发还要考虑URL编码、输出上下文和浏览器显示。

```html
<script>document.documentElement.dataset.labXss='yes'</script>
```

执行后在浏览器开发者工具检查`document.documentElement.dataset.labXss`是否为`yes`。存储型案例还要确认该输入经写入后由另一请求读出、渲染并执行；仅POST成功不能证明XSS。普通文本在页面出现并不等于脚本执行。

参考验证是由人建立真实标签的证据，保存到evidence/truth/Sxxx，和模型的POC证据目录分开。保存请求时去掉实际会话Cookie值；复现步骤注明如何重新登录获取有效会话。

## 五  接收模型POC后的检查

每条`run_id`建目录pocs/run_id。模型生成代码原样保存original.py或其实际语言扩展名，同时保存整个raw_output.txt。先阅读，不直接复制执行；逐项核对目标是否为127.0.0.1:4280、HTTP方法和参数是否与入口一致、是否包含文件删除或外发、是否需要Cookie与CSRF、成功断言是否真正对应漏洞影响。

验证可以分四种状态：

|状态|含义|记录动作|
|---|---|---|
|未执行|缺环境、依赖或脚本行为无法接受|保留原文和原因|
|原脚本直接执行|不改代码且正常运行|保存stdout、stderr、退出码与实际现象|
|只作环境适配|改本机地址、Cookie、令牌、文件路径|另存adapted版本及diff|
|修改验证逻辑|改请求流程、测试输入或成功断言|另存logic_fixed版本，成功不归给原POC|

记录中的raw_execution_ok、environment_execution_ok分别表示该阶段代码能正常执行；verification=triggered只有观察到既定漏洞影响才填。脚本执行成功但断言错误，必须写明失败。未报告漏洞的模型无需强行补一份POC；在正式记录里填poc_generated=false。

执行示例以真实生成的Python脚本为例，不能在未检查脚本时直接执行：

```bash
mkdir -p evidence/F_S007_V0_R1
python3 pocs/F_S007_V0_R1/original.py \
  > evidence/F_S007_V0_R1/stdout.txt \
  2> evidence/F_S007_V0_R1/stderr.txt
```

命令结束后另记录退出码和当时会话状态。如果模型给的是curl或PHP脚本，按其依赖执行并存原文。修订脚本时用`diff -u original.py adapted.py`保存修改差异；动态登录凭据不写入提交文件。

## 六  Burp Repeater联动的两例演示

一例使用SQLi的本机请求，一例使用XSS的本机请求。浏览器代理指向Burp，触发正常请求，在Proxy历史里确认host为127.0.0.1:4280，再发送到Repeater。手工只改一个参数并点击Send，保存正常与测试请求、响应及浏览器效果。

展示逻辑为“LLM指向某个参数和代码行→Burp重放该参数的正常/测试请求→本机观察差异→切换修复对照→相同方法复测”。Burp是手工请求观察工具，材料中注明没有用其自动扫描器对整站做性能评估。

XSS不能只靠Burp返回体断定代码执行，仍需浏览器证据。存储型XSS的写入与读取分别保存请求。将Cookie与CSRF值遮盖后归档，个人登录步骤写进复现说明。

## 七  给每位成员的验证模板

复制templates/verification.md填入：sample_id、run_id、执行人、模型判断、目标与前提、原始POC路径、脚本审阅结论、是否适配和diff、运行命令、状态码、业务对照、实际浏览器或数据库现象、验证结论、截图与日志路径、复核人。

建议每人先由D带着做一例，然后本人操作余下记录。D只复核异常环境情况，不替全组代跑。发现同一会话Cookie过期造成失败时，标环境故障并记录新会话重试；不要悄悄删除首次失败日志。

## 八  第二台电脑的复现与备份

第9天在另一成员电脑上，按version.txt配置Docker与仓库提交，导入教学数据，打开同一URL，按sample_card执行两个代表样本。对比本地与容器哈希、普通请求与测试请求，记录差异。

准备60—90秒录屏作为现场环境故障后的证据补充，但不替代实际验证。将模型原文、演示命令、样本卡、参考请求和截图放到demo目录；在登台前检查服务、登录状态、数据库和端口。

### D完成检查

官方仓库提交和镜像明确；本地与运行源码哈希一致；SQLi与XSS参考验证可重现；教学数据可恢复；每人知道怎样保存原始和修改POC；本人9条完成且C复核；A的9条已复核；两例Burp联动有请求与浏览器或数据库实证。

## 官方依据

DVWA安装与默认配置：https://github.com/digininja/DVWA
DVWA Compose：https://github.com/digininja/DVWA/blob/master/compose.yml
Burp Repeater：https://portswigger.net/burp/documentation/desktop/tools/repeater
