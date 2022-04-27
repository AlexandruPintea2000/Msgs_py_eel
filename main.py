from tkinter import filedialog, Tk


import numpy
import MySQLdb 
import pandas as pd
import matplotlib.pyplot as plt
from PIL import ImageTk, Image
import numpy as np
from scipy.interpolate import make_interp_spline
import eel


def on_close(page, sockets):
    print(page, 'closed')
    print('Still have sockets open to', sockets)

eel.init('web')


class User:
    def __init__ ( self, id, username, password, fullname, age, is_admin, email ):
        self.id = int( float( id ) );
        self.username = str( username );
        self.password = str( password );
        self.fullname = str( fullname );
        self.age = int( float( age ) );
        self.is_admin = int( float( is_admin ) );
        self.email = str( email );

    def strn ( self ):
        return "User( id=" + str( self.id ) + ", username='" + self.username + "', password='" + self.password + "', fullname='" + self.fullname + "', age=" + str( self.age ) + ", is_admin=" + str( self.is_admin ) + ", email='" + self.email + "' ) "; 

class Talk:
    def __init__ ( self, id, send_id, get_id, message ):
        self.id = int( float( id ) );
        self.send_id = int( float( send_id ) );
        self.get_id = int( float( get_id ) );
        self.message = str( message );

    def strn ( self ):
        return "Talk( id=" + str( self.id ) + ", send_id=" + str( self.send_id ) + ", get_id=" + str( self.get_id ) + ", message='" + self.message + "' ) "; 

    def json ( self ):
        return '{ "id":' + str( self.id ) + ', "send_id":' + str( self.send_id ) + ', "get_id":' + str( self.get_id ) + ', "message":"' + self.message + '" } '; 


def get_users ():
    conn = MySQLdb.connect( "localhost", "root", "thedb" )
    crs = conn.cursor();

    # execute SQL query using execute() method.
    crs.execute( "SELECT * FROM dbase.users ORDER BY id ASC;" )
    users_tuples = crs.fetchall()

    users_data = []
    for i in users_tuples:
        users_data.extend( i )

    conn.close();

    users = [];
    for i in range( len( users_data ) ):
        if ( i + 6 >= len( users_data ) ):
            break;

        if ( i % 7 != 0 ):
            continue;

        users.append( User( users_data[ i ], users_data[ i + 1 ], users_data[ i + 2 ], users_data[ i + 3 ], users_data[ i + 4 ], users_data[ i + 5 ] , users_data[ i + 6 ] ) );

    return users

def get_talks ():
    conn = MySQLdb.connect( "localhost", "root", "thedb" )
    crs = conn.cursor();

    # execute SQL query using execute() method.
    crs.execute( "SELECT * FROM dbase.talks ORDER BY id ASC;" )
    talks_tuples = crs.fetchall()

    talks_data = []
    for i in talks_tuples:
        talks_data.extend( i )

    conn.close();

    talks = [];
    for i in range( len( talks_data ) ):
        if ( i + 3 >= len( talks_data ) ):
            break;

        if ( i % 4 != 0 ):
            continue;

        talks.append( Talk( talks_data[ i ], talks_data[ i + 1 ], talks_data[ i + 2 ], talks_data[ i + 3 ] ) );

    return talks



def db_execute ( server, user, password, code ):
    db_conn = MySQLdb.connect( server, user, password )
    db_result = db_conn.cursor()

    db_result.execute( code )

    # print(db_result.fetchall())

    db_conn.commit()
    db_conn.close()


def get_talk_id ():
    talks = get_talks();
    for i in range( len( talks ) - 1 ):
        if ( talks[ i + 1 ].id - talks[ i ].id > 1 ):
            return talks[ i ].id + 1;
    return len( talks )

@eel.expose
def get_send_talks_for_user ( id ): # returns all talks that the user sent
    talks = get_talks();
    user_talks = "[ ";
    for i in range( len( talks ) ):
        if ( talks[ i ].send_id == id ):
            if ( user_talks != "[ " ):
                user_talks = user_talks + ", ";
            user_talks = user_talks + talks[ i ].json();
    user_talks = user_talks + " ]";
    return user_talks

@eel.expose
def get_get_talks_for_user ( id ): # returns all talks that the user got
    talks = get_talks();
    user_talks = "[ ";
    for i in range( len( talks ) ):
        if ( talks[ i ].get_id == id ):
            if ( user_talks != "[ " ):
                user_talks = user_talks + ", ";
            user_talks = user_talks + talks[ i ].json();
    user_talks = user_talks + " ]";
    return user_talks

def get_all_talks_for_user ( id ): # returns all talks that the user got
    talks = get_talks()
    user_talks = []
    for i in range( len( talks ) ):
        if ( talks[ i ].get_id == id ):
            # print("gets")
            user_talks.append(talks[i])
        if ( talks[ i ].send_id == id ):
            user_talks.append(talks[i])
    # print(user_talks)
    # print(talks)
    # print(id)
    return user_talks

@eel.expose
def add_talk ( send_id, get_id, message ):
    command = 'INSERT INTO dbase.talks VALUES ( ' + str( get_talk_id() ) + ', ' + str( send_id ) + ', ' + str( get_id ) + ', "' + message + '" );'
    db_execute( "localhost", "root", "thedb", command );

@eel.expose
def delete_talk ( id ):
    command = 'DELETE FROM dbase.talks WHERE id=' + str( id ) + ";";
    db_execute( "localhost", "root", "thedb", command );






def get_user_id ():
    users = get_users();
    for i in range( len( users ) - 1 ):
        if ( users[ i + 1 ].id - users[ i ].id > 1 ):
            return users[ i ].id + 1;
    return len( users )
 
@eel.expose
def get_user ( username, password ):
    users = get_users();
    for i in range( len( users ) ):
        if ( users[i].username == username and users[i].password == password ):
            return [ users[i].id, users[i].username, users[i].password, users[i].fullname, users[i].age, users[i].is_admin, users[i].email ];
    return -1

@eel.expose
def get_user_just_though_username ( username ):
    users = get_users();
    for i in range( len( users ) ):
        if ( users[i].username == username ):
            return [ users[i].id, users[i].username, users[i].password, users[i].fullname, users[i].age, users[i].is_admin, users[i].email ];
    return -1

@eel.expose
def get_user_just_though_id ( id ):
    users = get_users();
    for i in range( len( users ) ):
        if ( users[i].id == id ):
            return [ users[i].id, users[i].username, users[i].password, users[i].fullname, users[i].age, users[i].is_admin, users[i].email ];
    return -1

@eel.expose
def add_user ( username, password, fullname, age, is_admin, email ):
    users = get_users();
    for i in range( len( users ) ):
        if ( users[i].username == username ):
            # eel.load( "signup.html" );
            return 0; # username taken choose another one
    id = get_user_id();
    command = 'INSERT INTO dbase.users VALUES ( ' + str( id ) + ', "' + str( username ) + '", "' + str( password ) + '", "' + str( fullname ) + '", ' + str( age ) + ', ' + str( is_admin ) + ', "' + str( email ) + '" );'
    # # print(command);
    db_execute( "localhost", "root", "thedb", command );

    return [ id, username, password, fullname, age, is_admin, email ]; # username available, user was added

@eel.expose
def update_user ( id, username, password, fullname, age, is_admin, email ):
    command = 'UPDATE dbase.users SET username = "' + username + '", password = "' + password + '", fullname = "' + fullname + '", is_admin = ' + is_admin + ', email = "' + email + '" WHERE id = ' + str(id) + ';'
    db_execute( "localhost", "root", "thedb", command );


@eel.expose
def delete_user ( id ): # does not delete talks for some reason
    command1 = "DELETE FROM dbase.talks WHERE send_id=" + str( id ) + " OR get_id=" + str( id ) + ";";
    # print(command1)
    db_execute( "localhost", "root", "thedb", command1 );

    command2 = 'DELETE FROM dbase.users WHERE id=' + str( id ) + ';';
    db_execute( "localhost", "root", "thedb", command2 );







@eel.expose
def upload():
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    uploaded_file = filedialog.askopenfile()
    chart(read_file_to_variable(uploaded_file.name))


eel.start( "index.html", mode="chrome-app" )
