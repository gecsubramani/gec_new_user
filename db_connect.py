import psycopg2 as ps
import eel

@eel.expose
def con():
    try:
        db= ps.connect(
            host="ec2-52-54-212-232.compute-1.amazonaws.com",
            dbname ="d23jenlk8p1b9t",
            user="ceatsidfqpdhis",
            password="54d89dc110fc72199dd9680db6c31751f63f70ca6e3baf2def47f43e124edc0d",
            port="5432"
        )
        try:
            eel.addText("DATABASE connection successful")
        except:
            pass
        return db
    except Exception as e:
        try:
            eel.addText("DATABASE connection failed")
        except:
            pass
        return e


if __name__ == "__main__":
    con()




