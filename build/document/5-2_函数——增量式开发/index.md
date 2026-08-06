
除了教材的例子，我们可以把要实现的东西作为一个类，类里面放变量（性质）和函数（方法）

例如：
```c
class Enemy;
class Game1{ //class Game是声明，大括号里面是定义的内容。结构体struct也是这样，和class同源。不同之处：struct默认public，class默认private.
// game1.h实现的内容
    //实体
    Gui gui;
    std::list<Enemy*> enemies;
	    //计时器
    int cycle;
    int bombertick;
public:
	Game(int _row, int _col, int _tick);
    ~Game();
    void spawnEnemy();
//more..........

// game1.C实现的内容
void Game1::spawnEnemy(){//补足敌人
    if (cycle % (7*tick) == 0){
        if (gunboatCount < maxgunboat) {
            spawnObjects("Gunboat");
            gunboatCount++;
        }
        if (destroyerCount < maxdestroyer){
            spawnObjects("Destroyer");
            destroyerCount++;
        }
        if (cruiserCount < maxcruiser) {
            spawnObjects("Cruiser");
            cruiserCount++;
        }
    }
}
//more and more..........
};

//如果要实现多游戏切换，可以考虑再加一个类game2，然后实现一个gameloader选择一个游戏（其实就是array里面存 指向类的实例的指针，用的时候调用就行
```

为了管理方便 : ) ，当然也可以把函数的实现和变量的定义分开来写（见上文注释）