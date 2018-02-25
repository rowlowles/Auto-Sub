char dataString[50] = {0};
int a =0; 

void setup() {
Serial.begin(9600);              //Starting serial communication
}
  
void loop() {
  while(!Serial.available())
  {
    
  }
  Serial.read();
  Serial.println("Hello Pi");   // send the data
  delay(50);                  // give the loop some break
}
