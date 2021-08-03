### 介绍：

​		百度图片下载助手，能够个性化爬取[百度图片](https://image.baidu.com/)上的图片。

### 开发环境：

​	 	Pycharm（python3.8），第三方库：requests、selenium、multiprocessing、json

### 使用说明：

​		**共做了两个方案：**

（1）直接分析解码百度图片后台AJAX请求，直接爬取图片。这种方法虽简单，但容易被百度反爬机制发现，不太稳定。

（2）通过Selenium模拟浏览器操作来避免百度反爬，这种方法比较稳定。此外，通过多进程提高了效率。

