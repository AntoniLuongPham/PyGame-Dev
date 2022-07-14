from time import sleep

are_you_ready = str(input("are you ready? "))
done_with_timer = "no"
if (are_you_ready == "yes") and (done_with_timer == "no"):
    time = 120
    while time < 0:
        time =- 1
        sleep(1)
