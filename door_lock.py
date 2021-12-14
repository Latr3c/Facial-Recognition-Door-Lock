import face_recognition
import RPi.GPIO as GPIO
from subprocess import call
import time
# internet connection required
import speech_recognition as sr

def speak(text):
    """
    text to speech function
    """
    cmd_beg= 'espeak '
    cmd_end= ' | aplay /home/pi/Desktop/Text.wav  2>/dev/null' # To play back the stored .wav file and to dump the std errors to /dev/null
    cmd_out= '--stdout > /home/pi/Desktop/Text.wav ' # To store the voice file

    #Replacing ' ' with '_' to identify words in the text entered
    text = text.replace(' ', '_')

    #Calls the Espeak TTS Engine to read aloud a Text
    call([cmd_beg+cmd_out+text+cmd_end], shell=True)
    
def speech():
    r = sr.Recognizer()
    speech = sr.Microphone(device_index=2)
    with speech as source:
        speak("Hello, please enter your password")
        print("Say something!...")
        audio = r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        print("done")
    try:
        recog = r.recognize_google(audio, language = 'en-US')
        
        print("You said: " + recog)
        return recog
    except sr.UnknownValueError:
        print("Google Speech Recognition could not undertand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service: {0}".format(e))
    


def webcam(name):
    """
    use subprocess to take picture with webcam
    """
    # set command as a variable to insert variables
    cmd = "fswebcam --no-banner -r 680x480 {}.jpg".format(name)
    # sends the command to the terminal
    #os.system(cmd) Non sub process
    call([cmd], shell=True)
    filename= "/home/pi/"+str(name)+".jpg"
    return filename

def face():
    # Users that are already in the system need a picture and encoding.
    nathan_picture = face_recognition.load_image_file("/home/pi/Nathan1.jpg")
    nathan_encoding = face_recognition.face_encodings(nathan_picture)[0]
    ethan_picture = face_recognition.load_image_file("/home/pi/ethan.jpg")
    ethan_encoding = face_recognition.face_encodings(ethan_picture)[0]
    anne_picture = face_recognition.load_image_file("/home/pi/anne.jpg")
    anne_encoding = face_recognition.face_encodings(anne_picture)[0]
    
    #if unknown face is not recognized
    unknown_picture = face_recognition.load_image_file("/home/pi/ethan.jpg")
    unknown_face_encoding = face_recognition.face_encodings(unknown_picture)[0]
    
   # The list of user encoding with the assigned name.
    encodings = [ (ethan_encoding, 'Ethan'),(nathan_encoding, 'Nathan'),(anne_encoding, 'Anne')]

    

    try:
        # Prompts the user to enter their name on the kkeyboard.
        speak("Please type your name")
        name = input("Please enter your name: ")
        speak("Please look at the camera")
        # Wait 2 seconds for user to react
        time.sleep(2)
        filename = webcam(name)
    
        speak("Thank you")

        unknown_picture = face_recognition.load_image_file(filename)
        unknown_face_encoding = face_recognition.face_encodings(unknown_picture)

        names = [x[1] for x in encodings]
       
        if len(unknown_face_encoding) > 0:
           
            results = face_recognition.compare_faces([x[0] for x in encodings], unknown_face_encoding[0])
            user = ([names[x] for x in range(len(results)) if results[x]])
            return user[0]
        else:
            print("Couldn't find face")
            return "Unknown"
    except Exception as err:
      # Errors will be thrown off if the user does not have a webcam or i they do 
      # not grant page permission to acess it

        print(str(err))
    
        

        
def main():
    # Set up the GPIO pins.
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(21, GPIO.OUT)
    GPIO.setwarnings(False)
    
    person = face()
    
    print("Hello {}".format(person))
    if person != "Unknown":
        
        x = speech()
    
        if person == x:
            GPIO.output(21, GPIO.HIGH)
            text = "Welcome {}.".format(person)
            speak(text)
            print("Unlocked")
            time.sleep(5)
            GPIO.output(21, GPIO.LOW)
            

        else:
            GPIO.output(21, GPIO.LOW)
            text = "Incorrect password."
            speak(text)
        
    else:
        print("Face not recgonized")
        speak("Face not recgonzied.")
    
    speak("Goodbye")

    
        
if __name__ == "__main__":
    main()
