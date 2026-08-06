一下是一份约100lines的代码：

```c
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

// ---------- 矩阵结构体 ----------
typedef struct {
    int rows;
    int cols;
    int *data;      // 长度为 rows * cols
} Matrix;

typedef a;
struct Matrixs{
    int a;
};

// ---------- 创建 / 销毁 ----------
Matrix* matrix_create(int rows, int cols) {
    Matrix *m = (Matrix*)malloc(sizeof(Matrix));
    if (!m) return NULL;
    m->rows = rows;
    m->cols = cols;
    m->data = (int*)malloc(rows * cols * sizeof(int));
    if (!m->data) {
        free(m);
        return NULL;
    }
    return m;
}

void matrix_destroy(Matrix *m) {
    if (m) {
        free(m->data);
        free(m);
    }
}

define MAT_AT(m, i, j) ((m)->data[(i) * (m)->cols + (j)])

bool matrix_read(Matrix *m) {
    for (int i = 0; i < m->rows; ++i) {
        for (int j = 0; j < m->cols; ++j) {
            if (scanf("%d", &MAT_AT(m, i, j)) != 1)
                return false;
        }
    }
    return true;
}

// ---------- 打印矩阵 ----------
void matrix_print(const Matrix *m, const char *name) {
    printf("%s : (row %d, col %d)\n\n", name, m->rows, m->cols);
    for (int i = 0; i < m->rows; ++i) {
        for (int j = 0; j < m->cols; ++j) {
            printf(" %d", MAT_AT(m, i, j));
        }
        printf("\n");
    }
    printf("\n");
}

Matrix* matrix_multiply(const Matrix *A, const Matrix *B) {
    if (A->cols != B->rows) {
        printf("Dimension mismatch: A.cols(%d) != B.rows(%d)\n", A->cols, B->rows);
        return NULL;
    }

    Matrix *C = matrix_create(A->rows, B->cols);
    if (!C) return NULL;

    int *c_ptr = C->data;
    for (int i = 0; i < A->rows; ++i) {
        for (int j = 0; j < B->cols; ++j) {
            int sum = 0;
            // 计算 C[i][j]
            for (int k = 0; k < A->cols; ++k) {
                sum += MAT_AT(A, i, k) * MAT_AT(B, k, j);
            }
            *c_ptr++ = sum;
        }
    }
    return C;
}

// ---------- 主程序 ----------
int main() {
    int ar, ac, br, bc;
    if (scanf("%d %d %d %d", &ar, &ac, &br, &bc) != 4) {
        fprintf(stderr, "Failed to read dimensions.\n");
        return 1;
    }

    Matrix *A = matrix_create(ar, ac);
    Matrix *B = matrix_create(br, bc);
    if (!A || !B) {
        fprintf(stderr, "Memory allocation failed.\n");
        matrix_destroy(A);
        matrix_destroy(B);
        return 1;
    }

    if (!matrix_read(A) || !matrix_read(B)) {
        fprintf(stderr, "Failed to read matrix data.\n");
        matrix_destroy(A);
        matrix_destroy(B);
        return 1;
    }

    Matrix *C = matrix_multiply(A, B);
    if (!C) {
        matrix_destroy(A);
        matrix_destroy(B);
        return 1;
    }

    matrix_print(A, "matrix_a");
    matrix_print(B, "matrix_b");
    matrix_print(C, "matrix_c");

    matrix_destroy(A);
    matrix_destroy(B);
    matrix_destroy(C);
    return 0;
}
```

《Linux C编程一站式学习》提到，阅读代码不能像看小说或者看题目一样从头读到尾，需要从主干到枝叶；在学习过程中，可以通过画函数之间的关系图、看函数和变量名帮助理解代码的行为。

# main函数是程序入口
我们知道，在C/C++中，main函数是程序入口，终端每次运行C/C++编译后的可执行文件，会从main函数执行，以main函数返回数值而宣告程序的结束。所以阅读代码可以从main函数开始，看他里面定义了什么变量，调用了什么函数。

可以看到，main函数里面使用了`scanf`这一标准输入函数，`fprintf`这一输出函数(专门用于输出报错信息)

# 一个合格的程序，至少要有输出，最好要有输入
为什么？可以上网搜。
根据这一点，程序的重要关注部分就是==输入的格式、输出的内容==。或许有时候看不到输出的内容，他们被封装在其他函数里面，让这个函数专门用于实现输出功能。比如，从关键词"print"可以看出，这个程序的`matrix_print`很可能实现了一部分输出内容，此时溯源定位原函数位置，发现确实如此。


| **类比** | 输入(Input) | 输出(Output)      |
| ------ | --------- | --------------- |
| 程序     |           |                 |
| 函数     | 传参        | 返回值/直接修改传入的参数引用 |
| AI模型   | 张量        | 张量              |
|        |           |                 |

---
# 这么多return看起来眼花缭乱

有人说，main函数里面这么多return，返回值还不一样，究竟返回第几个呢？

首先，一个合格的代码不会只运行第一个return，让后面的代码永远得不到运行。

注意看，前面4个return都被包裹在if控制下的代码块里面。（代码块里面的变量和函数在程序执行到末尾时就会清除）当一种条件成立，进入代码块运行相应代码并return结束main函数，后面的代码块不会被运行。这样就变相实现了if--else的功能，也更美观。

在工程中，==单独列出的if条件用于排除一些特例，而循环结构更能使得程序千变万化，实现更丰富的功能。==因此阅读过程中， 看完的if分支即可选择性忽略，在心中给代码进行剪枝以突出代码核心功能。

---
# 程序跳读：看完main看有关的函数
暂时忽略掉if-else分支后，我们把注意力集中在`matrix_create` `matrix_print` `matrix_destroy` 这三个函数。

## matrix_create()
虽然他见缝插针在if代码块之间，但是却很重要。
我们可以通过`ctrl+f`定位到所有地方，找定义函数的语法以跳到这个函数的位置。

在这个函数中，我们可以看到：`if xxxxx, return NULL;` 这其实是一种“检查不通过，返回零值表示不存在、不合法的情况。（在python则可以用 return None)

- `Matrix *m = (Matrix*)malloc(sizeof(Matrix));`
这里是一个等式，先看等号右边。
等号右边是malloc动态开辟内存的语法，官方定义这种函数传入开辟空间的大小(单位为byte，这里传入大小`sizeof(Matrix)`），返回开辟空间的第一个内存地址。由于默认为`void*`，需要通过(Matrix*)实现转换。
等号左边是新定义的指针m，规定需要指向结构体Matrix.

**易错**：把`(Matrix*)` 写成`(Matrix)` .这样就试图把指针`void*`转换为结构体`Matrix`，很可能报错。

- `m->data = (int*)malloc(rows * cols * sizeof(int));`
类似，开辟大小为`rows * cols * sizeof(int)`的空间P，传给指针data(这里data属于实例M的对象，其中指针m指向他)，调用这个data需要`(*m).data`（先访问指针m指向的结构体，再访问所属的对象data, 简化语法后就是这样`m->data` 。

可以理解为：
```c
int &*v = (int*)malloc(rows * cols * sizeof(int));
m->data = v;
```
![[Pasted image 20260706085943.png]]


如果注释够多，我们也对矩阵定义熟悉的话，就可以知道matrix_create()可以创建一个矩阵，把开辟的空间data、row和col用结构体打包，方便管理和调用。


---
## matrix_read()
一开始我想先讲`matrix_multiply()`，但是发现后面也有宏定义`MATAT`，那么还是先从代码量少的matrix_read开始。

---
## matrix_multiply()

multiply：乘法。

这里假设读者学过矩阵。我们看矩阵一般就是一个有行有列的数字阵。代码也是希望这么维护的，从row, col, `MATAT`都能看出来。这里维护一个二维矩阵，进行乘法。

把变量k的for循环提到最外层，减少跳跃读取，增加缓存命中率。

[[main|返回]]
