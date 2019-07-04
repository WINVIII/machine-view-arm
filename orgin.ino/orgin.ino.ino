#include <Servo.h>
#define servo1 8    //右臂
#define servo2 9    //底座
#define servo3 10   //爪子
#define servo4 11   //前臂
Servo s1, s2, s3, s4 ; //定义舵机号
int servostep = 2;   //灵敏度，舵机每一步移动角度
int ss;
int speed_=0;
/* {a,b,c,d,e}
   a 舵机复位初始角度
   b 舵机运行最小角度
   c 舵机运行最大角度
   d 舵机正反
   e 舵机移动延时，数字越大移动速度越慢，增加可控性
*/
int s1angle[] = {90, 0, 100, 0, 15}; //右臂  越小越向下
int s2angle[] = {100, 0, 180, 1, 15}; //底座 越小越向右
int s3angle[] = {90, 80, 170, 0, 15}; //爪子 越小越闭合
int s4angle[] = {90, 90, 150, 0, 15}; //前臂 越小越往前
int s1step = s1angle[0], s2step = s2angle[0], s3step = s3angle[0], s4step = s4angle[0];
unsigned long s1millis = 0, s2millis = 0, s3millis = 0, s4millis = 0; //初始化舵机运行时间，用于计算时间差使机械臂运动变慢
int s1curangle, s2curangle, s3curangle, s4curangle;              //舵机当前角度位置
int serialmode = 0;

void setup() {
  Serial.begin(9600);                                           //串口通信是否打开
  pinMode(servo1, OUTPUT); pinMode(servo2, OUTPUT); pinMode(servo3, OUTPUT); pinMode(servo4, OUTPUT); //定义引脚
  s1.attach(servo1); s2.attach(servo2); s3.attach(servo3); s4.attach(servo4); //引脚绑定
  s1.write(s1angle[0]); s2.write(s2angle[0]); s3.write(s3angle[0]); s4.write(s4angle[0]); //初始位置
  s1curangle = s1angle[0];
  s2curangle = s2angle[0];
  s3curangle = s3angle[0];
  s4curangle = s4angle[0];
  /* analogRead 读取从手柄接收的值
     map        将手柄接收的值映射到区间，使其大于最小角度，小于最大角度
  */
  s1angle[0] = (map(analogRead(A0), 0, 1023, s1angle[1], s1angle[2])); //手柄控制接收
  s2angle[0] = (map(analogRead(A1), 0, 1023, s2angle[1], s2angle[2]));
  s3angle[0] = (map(analogRead(A2), 0, 1023, s3angle[1], s3angle[2]));
  s4angle[0] = (map(analogRead(A3), 0, 1023, s4angle[1], s4angle[2]));


}


/*整形函数，返回值：舵机下一步将要移动到的位置
   getposition(a,b,c,d,e)
   a 引脚
   b 设定参数
   c 最小角度
   d 最大角度
   e 需要移动的位置
*/
int getposition(uint8_t ana_pin, int &init_angle, int min_angle, int max_angle, int s_curangle) { //每步运行轨迹
  int curangle = s_curangle;
  int stgmove;
  if (ana_pin != 0) {
    stgmove = map(analogRead(ana_pin), 0, 1023, min_angle, max_angle);
  } else {
    stgmove = init_angle;
  }
  if (stgmove - curangle > servostep && stgmove - init_angle > 2) curangle += servostep;
  if (curangle - stgmove > servostep && init_angle - stgmove > 2) curangle -= servostep;
  if (curangle > min_angle && curangle < max_angle) {                          //移动不超出舵机设定范围
    return curangle ;
  } else return s_curangle;
}


int StringToInteger(char *p)//传入数字提取
{
  int value = 0;
  while (*p != '\0')
  {
    if ((*p >= '0') && (*p <= '9'))
    {
      value = value * 10 + *p - '0';
    }
    p++;

  }
  return value;
}

int nextstep(int start, int finish)
{
  if (finish > start)
  {
    return start + 1;
  }
  if (finish < start)
  {
    return start - 1;
  }else
  {
    return finish;
  }
}

void loop() {
  if (Serial.available() > 0) {     //串口通讯模块
    /*输入说明：
      qb=90
      前臂运行到90度
      同理：yb 右臂
            dz 底座
            zz 爪子
    */
    serialmode = 1;
    char command[5] = "aaaaa"; //串口接收到数据
    Serial.readBytes(command, 5); //获取串口接收到的数据
    int num = 90;
    char *p = command;
    num = StringToInteger(p);
    //将传入数据中数字提取
    if (command[0] == 'Y' || command[0] == 'y')
    {
      s1angle[0] = num;
    }
    if (command[0] == 'd' || command[0] == 'D')
    {
      s2angle[0] = num + 10; //底盘因舵机安装误差问题角度+10
    }
    if (command[0] == 'z' || command[0] == 'Z')
    {
      s3angle[0] = num;
    }
    if (command[0] == 'Q' || command[0] == 'q')
    {
      s4angle[0] = num;
    }
    if (command[0] == 's' || command[0] == 'S')
    {
      speed_=1;
    }
    if (command[0] == 'r' || command[0] == 'R')
    {
      s1angle[0] = 90;
      s2angle[0] = 100;
      s3angle[0] = 80;
      s4angle[0] = 90;
    }
  }

  //右臂
  if (millis() >= s1millis) {
    if (serialmode == 0) {    //判断电脑串口是否打开
      ss = getposition(A0, s1angle[0], s1angle[1], s1angle[2], s1curangle);
    } else if (serialmode == 1) {
      if (speed_==1){
      ss=s1angle[0];
      }else{
      s1step = nextstep(s1step, s1angle[0]);
      ss=s1step;
      }
    }
    if (abs(s1curangle - ss) >= servostep) {
      s1curangle = ss;
      s1.write(s1angle[3] > 0 ? ss : 180 - ss);
      s1millis = millis() + s1angle[4];
    }
  }

  //底座
  if (millis() >= s2millis) {
    if (serialmode == 0) {
      ss = getposition(A1, s2angle[0], s2angle[1], s2angle[2], s2curangle);
    } else if (serialmode == 1) {
      if (speed_==1){
      ss=s2angle[0];
      }else{
      s2step = nextstep(s2step, s2angle[0]);
      ss=s2step;
      }
    }
    if (abs(s2curangle - ss) >= servostep) {
      s2curangle = ss;
      s2.write(s2angle[3] > 0 ? ss : 180 - ss);
      s2millis = millis() + s2angle[4];
    }
  }
  //爪子
  if (millis() >= s3millis) {
    if (serialmode == 0) {
      ss = getposition(A2, s3angle[0], s3angle[1], s3angle[2], s3curangle);
    } else if (serialmode == 1) {
      ss=s3angle[0];
    }
    if (abs(s3curangle - ss) >= servostep) {
      s3curangle = ss;
      s3.write(s3angle[3] > 0 ? ss : 180 - ss);
      s3millis = millis() + s3angle[4];
    }
  }
  //前臂
  if (millis() >= s4millis) {
    if (serialmode == 0) {
      ss = getposition(A3, s4angle[0], s4angle[1], s4angle[2], s4curangle);
    } else if (serialmode == 1) {
      if (speed_==1){
      ss=s4angle[0];
      }else{
      s4step = nextstep(s4step, s4angle[0]);
      ss=s4step;
      }
    }
    if (abs(s4curangle - ss) >= servostep) {
      s4curangle = ss;
      s4.write(s4angle[3] > 0 ? ss : 180 - ss);
      s4millis = millis() + s4angle[4];
    }
  }
}
