# 什么是结构体

结构体可以视为**变量的集合**。一个结构体通过捆绑变量，实现变量的统一管理。
以下是一个结构体在C语言的**定义**：

```c
typedef struct {
    int rows;
    int cols;
    int *data;
} Matrix;
```
这里的`typedef`是C语言用于声明一个新类型(int, double都属于数据类型)的指令。
由于C语言根据分号和关键字断句，左花括号可以放在`struct`的下一行，但是工程上习惯如实例代码进行放置。
# 如何使用结构体

- 1.实例化一个结构体。我们可以从“实例化”这个操作，以及C语言关键字`typedef`理解到：一个结构体就是一个类型。类似`int name`，结构体的使用如下：
```c
//声明一个结构体（并且【按顺序】声明结构体里面的变量与初始化）
Matrix mat;
//初始化
mat.rows = 1;
mat.cols = 1;
mat.data = (int*)malloc(mat.rows * mat.cols * sizeof(int));

```

