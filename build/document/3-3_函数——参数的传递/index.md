# 习题1
在调用函数时，参数`通过复制（默认）`或`传递其引用`来传递。

```c
void increment(int x)
{
	x = x + 1;
}

int main(void)
{
	int i = 1, j = 2;
	increment(i); /* i now becomes 2 */
	increment(j); /* j now becomes 3 */
	return 0;
}
```

| 序号  | 操作（对应行）            | 内存中的变量                  |     |     |
| --- | ------------------ | ----------------------- | --- | --- |
| 1   | 声明并复制i, j          | i=1, j=2                |     |     |
| 2   | increment(i)--入栈   | i=1, j=2, increment_x=1 |     |     |
| 3   | increment(i)--执行自加 | i=1, j=2, increment_x=2 |     |     |
| 4   | increment(i)--出栈   | i=1, j=2                |     |     |
| 5   | increment(j)--入栈   | i=1, j=2, increment_x=1 |     |     |
| 6   | increment(j)--执行自加 | i=1, j=2, increment_x=2 |     |     |
| 7   | increment(j)--出栈   | i=1, j=2                |     |     |
| 8   | return 0; 之后       | 空                       |     |     |

# 习题2
如果在一个程序中调用了`printf`函数却不包含头文件，例如`int main(void) { printf("\n"); }`，编译时会报警告：`warning: incompatible implicit declaration of built-in function ‘printf’`。请分析错误原因。

- **头文件与实现的区分：** 我们要明确一点：`<stdio.h>` 头文件中只包含了 `printf` 的**函数声明（原型）**，用于编译期的类型检查；而 `printf` 的真正**代码实现**位于系统的标准C库（libc）中，由链接器负责接入。
    
- **早期C标准（C89/C90）的处理机制 —— 为什么是 Warning？**
    [Hypothesis](https://hypothes.is/a/A0jzssywEemSol95zyJm3w)
    - **隐式声明（Implicit Declaration）：** 当编译器看到一个没有提前声明的函数时，它不会立刻报错，而是按照规则自动生成一个“隐式声明”，即假定该函数返回 `int` 类型，且不限制参数类型（类似于 `int printf();`）。
        
    - **内建函数冲突（Built-in Function）：** 现代编译器（如GCC）为了优化性能，内部自带了 `printf` 等常用标准库函数的模型（即内建函数）。编译器内部知道 `printf` 的真实原型是 `int printf(const char * restrict format, ...);`。
        
    - **报错原因总结：** 编译器自己生成的“隐式声明”，与它内部记录的“内建函数原型”在参数类型（比如缺乏 `restrict` 限定符和不定参数标识）上**不兼容（incompatible）**，因此抛出此特定警告。
        
- **现代C标准（C99及以后）的变化 —— 为什么变成了 Error？**
    [Linux C一站式编程习题答案 - 立体风 - 博客园](https://www.cnblogs.com/litifeng/articles/5638574.html) 
    - 现代C语言标准（C99开始，并在现代编译器如 GCC 14 / Clang 15 中严格执行）**彻底废除了隐式函数声明**。
        
    - 在现代环境下编译相同的代码，不再是报警告，而是直接引发编译终止的**致命错误 (Error)**。报错信息通常为：`error: implicit declaration of function 'printf' is invalid in C99`（不允许隐式声明函数）。这就强制要求程序员在使用任何函数前，必须严格提供对应的头文件或显式声明，保障了代码的类型安全。

[ISO/IEC JTC1/SC22/WG14 - C](https://www.open-std.org/jtc1/sc22/wg14/)
[ISO/IEC 9899:2023](https://www.open-std.org/jtc1/sc22/wg14/www/docs/n3096.pdf)

