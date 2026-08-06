难度：入门lv5.0，上手lv13.8(为什么不是13.9 or 13.7呢，好难猜啊)

## 0. 常见的工程项目结构

一个规范的 C/C++ 工程项目通常包含以下结构：

```c
LICENSE       # 如果在项目中发布源码，建议包含一份开源协议。未指定协议时他人通常无权使用。
README.md     # 项目说明文档（Markdown 格式）。
Makefile      # 项目的核心构建自动化脚本。
bin/          # 存放最终生成的可执行程序（通常初始为空，由 Makefile 生成）。
build/        # 存放中间编译产物（如 .o 库文件，通常初始为空）。
src/          # 存放源代码文件（如 .c 和 .h）。
tests/        # 存放自动化测试代码。
assets/       # 存放项目静态资源（图片、数据等）。
```

---

# Why choose makefile ?

## 1. 便于一键使用编译命令
- 帮助我们在几天后或几个月后还能记得怎么编译并使用项目。
- 方便别人一键部署源代码并且使用
	- 为了节约空间和时间，传输项目一般不会包括可执行文件。
	- 类似的思想：requirement.txt，里面可能放了很多的pip install xxx，便于到手后灵活使用（比如过几天给电脑腾出空间了再使用）
	
```makefile
app: main.o hello.o
	gcc main.o hello.o -o app

main.o: main.c
	gcc -c main.c -o main.o

hello.o: hello.c
	gcc -c hello.c -o hello.o

clean:
	rm -f main.o hello.o app
```

---
## 2. 写好脚本，先构思再行动
- 写脚本方便管理要运行的指令，能更好把握计算机的行为 （你喜欢以下行为吗）

```bash
gcc -o main main.o sub1.o sub2.o
gcc -c sub1.o sub1.c
# 报错---找不到源文件 or 编译错误
# 频繁按 Up 方向键翻找上一条命令...
......
./main -g
```

- 看看更高效的工作流，这样方便一些吧！
```bash
pico main.c
make
./main
```

- 与shell结合一下
```shell
source ./test.sh #这里面可以包装指令，构建程序行为，也方便工程传递，开箱即用
```
test.sh:
```shell
make clean
make
./main [自定义参数]
```

---
## 3. 分离相同命令，复用行为
### 请记住基本的指令行为：
```c
目标(target)...: 依赖(prerequisites)...
	命令(command)
#注意是<Tab>不是4个空格字符；Vscode会正确翻译成<Tab>而不是4个空格的。
```

- 和选项1的原始代码看看有何不同 (看变量的引入和百分号%的使用)

```c
TARGET = mygame 
all: $(TARGET)

$(TARGET): main.o Game.o Gui.o Battleship.o Shell.o Enemy.o Gunboat.o Destroyer.o Island.o Cruiser.o Bomber.o Missile.o Pack.o
	g++ -Wall -g -o $(TARGET) main.o Game.o Gui.o Battleship.o Shell.o Enemy.o Gunboat.o Destroyer.o Island.o Cruiser.o Bomber.o Missile.o Pack.o -lncurses

%.o: %.C
	g++ -Wall -g -c $< -o $@

clean:
	rm -f main.o Game.o Gui.o Battleship.o Shell.o Enemy.o Gunboat.o Destroyer.o Island.o Cruiser.o Bomber.o Missile.o Pack.o mygame
```

- **模式匹配（`%.o: %.C`）：** 彻底消灭了所有形如 `main.o: main.C`、`Game.o: Game.C` 的重复规则。无论未来项目扩展到几十还是上百个 `.C` 文件，全都会自动套用这同一套编译<mark>行为</mark>。 (行为：比如这里的-g, -Wall.....)
    
- **自动化变量（`$<` 与 `$@`）：**
    
    - `$<` 代表当前触发规则的**第一个依赖**（即具体对应的 `.C` 源文件）。
        
    - `$@` 代表当前触发规则的**目标**（即对应的 `.o` 文件）。
        
- **目标变量解耦（`TARGET`）：** 将最终可执行程序的文件名提取为 `TARGET = mygame`。后续更换项目名称时，只需修改顶部一处配置。


- ⚠️错误示范如下：(是我粘贴过来的时候没有改好)
```c
TARGET = mygame

all: $(TARGET)
$(TARGET): main.o Game.o Gui.o Battleship.o Shell.o Enemy.o Gunboat.o Destroyer.o Island.o Cruiser.o Bomber.o Missile.o Pack.o
	g++ -Wall -g -o $(TARGET) main.C Game.C Gui.C Battleship.C Shell.C Enemy.C Gunboat.C Destroyer.C Island.C Cruiser.C Bomber.C Missile.C Pack.C -lncurses

%.o: %.C
	g++ -Wall -g -c $< -o $@

clean:

	rm -f main.o Game.o Gui.o Battleship.o Shell.o Enemy.o Gunboat.o Destroyer.o Island.o Cruiser.o Bomber.o Missile.o Pack.o

	rm -f main.C Game.C Gui.C Battleship.C Shell.C Enemy.C Gunboat.C Destroyer.C Island.C Cruiser.C Bomber.C Missile.C Pack.C
```

---

## 4.用变量名简洁表达

```python
SRCS = main.C Game.C Gui.C Battleship.C Shell.C Enemy.C Gunboat.C Destroyer.C Island.C Cruiser.C Bomber.C Missile.C Pack.C
OBJS = $(SRCS:.C=.o) #这里是把SRC里面提到的.C文件映射为.o文件，方便表述
TARGET = mygame

all: $(TARGET)

$(TARGET): $(OBJS)
	g++ -Wall -g -o $(TARGET) $(OBJS) -lncurses

%.o: %.C
	g++ -Wall -g -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)

# 这里可以理解为把all clean作为保留词，不当作一个文件名all.C (不加也行)
# 没谁会起名这种"general"的名字吧！
.PHONY: all clean 
```

- 假如还想偷懒或者不想在文件的“正文”看到具体的参数（比如选用的编译工具g++, 编译模式-g....)
```c
CXX = g++
CXXFLAGS = -Wall -g
LDFLAGS = -lncurses

SRCS = main.C Game.C Gui.C Battleship.C Shell.C Enemy.C Gunboat.C Destroyer.C Island.C Cruiser.C Bomber.C Missile.C Pack.C

OBJS = $(SRCS:.C=.o)
TARGET = mygame

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(OBJS) $(LDFLAGS)

%.o: %.C
	$(CXX) $(CXXFLAGS) -c $< -o $@

clean:
	rm -f $(OBJS) $(TARGET)
```

<mark>注意</mark>：
选项1讲了“最初的makefile"用于偷懒，
选项2讲了假设构建好makefile和shell文件后的使用方法
选项3, 4讲了用模式匹配（隐式规则）和变量修饰来使得makefile更简洁可读（但是不一定什么都需要用变量名包装）
选项3只是 作用于模式复用，而真正的Target, Source还是需要自己写出来。

这里介绍一下自动search项目文件的方法，需要的同学可以STFW or STFAI

## 5. wildcard 函数自动搜集源文件
- `$(wildcard *.c)`：获取目录下所有的 `.c` 文件列表（例如 `main.c hello.c`）。
- `$(patsubst %.c, %.o, $(SRCS))`：把列表中所有的 `.c` 替换为 `.o`（例如 `main.o hello.o`）。

- 那么，上述的变量SRC和OBJS可以这么改：
```python
SRCS = $(wildcard *.c)
OBJS = $(patsubst %.c, %.o, $(SRCS))
```

## 6.其他小技巧
- 在命令前加 `@`，可以避免命令被终端打印出来，只输出执行命令里面的具体内容的反馈。
```shell
clean:
	@echo "Cleaning up build artifacts..."
	@rm -f $(OBJS) $(TARGET)
	@echo "Zzzzzz..."
```


## 7. Warning & Error
| **现象 / 报错信息**                                          | **公式层面的根本原因**                                               | **Make 的底层思考逻辑**                                 | **解决/排查方向**                                         |
| ------------------------------------------------------ | ----------------------------------------------------------- | ------------------------------------------------ | --------------------------------------------------- |
| **`'app' is up to date.`**                             | `target` 存在，且其时间戳**新于或等于**所有 `prerequisites`。               | “所有的源文件都没改过，`app` 已经是最新产物，不需要重新编译。”              | 若修改了 `.h` 仍提示此报错，说明 Makefile 未将 `.h` 写进依赖关系。        |
| **`missing separator. Stop.`**                         | `command` 行开头**没有使用严格的 `Tab` 键**（误用了空格）。                    | “我无法识别这一行是属于上面 `target` 的命令，语法分隔失败。”             | 检查命令行首，确保是 `\t` 而非空格。                               |
| **`No rule to make target 'X', needed by 'Y'. Stop.`** | 目标 `Y` 需要依赖 `X`，但磁盘上**无 `X` 文件**，且 Makefile 中**无 `X:` 规则**。 | “我要造 `Y` 必须先拿到 `X`，但我找不到 `X`，也不知道怎么造 `X`，依赖链断裂。” | 检查 `X` 是否拼写错误、文件是否被删、或是否漏写了 `%.o: %.c` 这类规则。        |
| **`'clean' is up to date.`** (运行 `make clean` 却不清理)    | 规则写为 `clean:`（依赖为空），且**当前目录下恰好存在名为 `clean` 的文件/文件夹**。       | “`clean` 目标存在，且没有依赖文件比它更新，我认为它已是最新，跳过命令。”        | 在 Makefile 中添加 `.PHONY: clean` 显式声明其为伪目标，强制忽略时间戳检查。 |

至于makefile调用makefile等其他进阶行为，请STFW or STFAI
至于为啥不使用shell来记录编译文件而是用makefile，原因至少有：makefile可以check哪些源码没有被修过，就不重复编译那一部分源码。makefile在编译时是多线程的（自动维护），编译量一多了效果自然可观。

makefile的知识，现在看起来似懂非懂没关系，至少要会用整洁的脚本定义一批指令，完成一个小任务，写脚本的时候，多想多构思，等到XPU跑起来，能解放双手亿会会，那才是真的爽！

（那些奇怪的语法和指令，用到了再说吧！）
（别找我，自行STFW和STFAI吧！）