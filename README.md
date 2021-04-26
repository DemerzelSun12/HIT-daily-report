# HIT-daily-report

基于Github Action的定时HIT疫情上报脚本，开箱即用

感谢 @JalinWang 提供[原始版本(用于深圳校区)](https://github.com/JalinWang/HITsz-daily-report)。

感谢 @billchenchina 提供的统一身份认证插件[hitutil](https://github.com/billchenchina/hitutil)
                          及[原始版本(本部)](https://github.com/billchenchina/yqxx)。

[手动疫情上报系统入口](https://xg.hit.edu.cn/zhxy-xgzs/xg_mobile/xs/yqxx)

## 使用方法

- fork仓库
- 设置仓库的action secret，添加用户名username、密码password和可选的API_KEY（详细步骤见后文）
- 开启Action（详细步骤见后文）
- 每天早上8:00（UTC 00:00)可自动定时运行，如果填写API_KEY，即可在微信上收到运行结果推送

消息推送Key申请地址：[Server酱](http://sc.ftqq.com/)

设置仓库的action secret，添加用户名username、密码password和可选的API_KEY：

| Name          | Value                                |
| ------------- | ------------------------------------ |
| username      | 统一身份认证密码 （学号）        |
| password      | 统一身份认证密码                 |
| API_KEY       | server酱推送的sckey                   |

![添加Action Secret的步骤](./image/instruction.png)

据说fork的仓库会默认关闭action的执行，需要在仓库设置里打开：
![启用Action的步骤1](./image/enable1.png)
![启用Action的步骤1](./image/enable2.png)

以上步骤都完工后可以手动运行一次工作流，验证是否可以正常工作
![手动运行](./image/test_run.png)

## 如果脚本挂了，或者你想修改一下上报地点什么的

`post_data.jsonc`里边是上报数据包的原始数据，修改之即可。
