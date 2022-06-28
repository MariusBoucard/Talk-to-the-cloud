#!/usr/bin/python3
import os
import sys
import easywebdav
from pprint import pprint
from termios import NCC

# in this example we disable SSL
import urllib3
urllib3.disable_warnings()

import nextcloud_client
from nextcloud import NextCloud

class NCConnect() :
    def __init__(self,url="Unknown",username="Unknown",password="Unknown") :
        #Possibilité de récuperer direct dans les settings

        nc = nextcloud_client.Client('https://'+url)
        nc.login(username,password)
        self.NEXTCLOUD_URL = "http://{}:80".format(url)
        self.NEXTCLOUD_USERNAME = username
        self.NEXTCLOUD_PASSWORD = password
        self.instance = NextCloud(
                self.NEXTCLOUD_URL,
                user=self.NEXTCLOUD_USERNAME,
                password=self.NEXTCLOUD_PASSWORD,
                session_kwargs={
                    'verify': False # False to disable ssl
                    })
        self.ncnew = nc

# see api_wrappers/webdav.py File definition to see attributes of a file
# see api_wrappers/systemtags.py Tag definition to see attributes of a tag
    def downloadpath(self,a,fileadr):
        self.wd=resource_path(os.getcwd())
        os.chdir(a)
        try :
            f = self.instance.get_file(fileadr)
            print(fileadr)
            f.fetch_file_content()
            f.download()
            os.chdir(self.wd)
        except ValueError :
            os.chdir(self.wd)
            print("dejadl")
        os.chdir(self.wd)
        #Telecharge direct dans la directory, peut etre moyen de diriger ca en tmp
        return f

        pass
    def pathFile(self,path):
        #Recup le path dans les settings
        self.path = path
        pprint(self.instance.list_folders(path).data)

    def upload(self,loc,dist):
        self.ncnew.put_file(dist,loc)
        #self.ncnew.put_file(str(loc),str(dist))
        print("cock")
        # pprint(self.instance.upload_file(loc,dist).data)
        #self.instance.upload_file(loc,dist)

    # list folder (get file path, file_id, and ressource_type that say if the file is a folder)
   
    # list folder with additionnal infos (the owner, if the file is a favorite…)
    # pprint(nxc.list_folders('/', all_properties=True).data)

    # list all files


    
    #Peut servir fort fort pour lister recursivement tous les records a ecouter (date supp et gestion de folder
    
    def _list_rec(self,d, indent=""):
        
        print(self.path)
            # list files recursively
        print("%s%s%s" % (indent, d, '/' if d.isdir() else ''))
        if d.isdir():
            for i in d.list():
                self._list_rec(i, indent=indent+"  ")
        else :
            self.liste.append(d)

    def recuperation(self) :
            #Variable du fichier à recup par le liste. rec
            file = ""
            self.liste=[]
            self._list_rec(self.instance.get_folder(self.path))
            return self.liste
        
    def getFileList(self,path):
        root = self.instance.get_folder(path)
        self.liste2=[]
        self._list_rec2(root)
        return self.liste2


    def _list_rec2(self,d, indent=""):
        
     
            # list files recursively
        print("%s%s%s" % (indent, d, '/' if d.isdir() else ''))
        if d.isdir():
            for i in d.list():
                self._list_rec2(i, indent=indent+"  ")
        else :
            self.liste2.append(d)
        pass
    def downloadtmp(self, file):
        self.wd=resource_path(os.getcwd())
        os.chdir('/tmp')
        try :
            f = self.instance.get_file(file)
            print(file)
            f.fetch_file_content()
            f.download()
            os.chdir(self.wd)
        except ValueError :
            os.chdir(self.wd)
            print("dejadl")
        os.chdir(self.wd)
        #Telecharge direct dans la directory, peut etre moyen de diriger ca en tmp
        return f
        print(f)
                #save F file to temps file /encours
    def getPath(self) :
            return self.path

def resource_path(relative_path):
    
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
    
if __name__ == '__main__':
    pass

    # upad
    #Upload direct dans les notes et print un .MD sympa pour tout t expliquer ce qu'il se passe
    #Creation de fichier type dans lequel on rentre des variables qui sont initialisées un peu comme a la compilation ?
    # pprint(nxc.create_folder('testdir_nextcloud').data)
    # pprint(nxc.upload_file('localfile.txt', 'testdir_nextcloud/localfilesend.txt').data)

    # # download
    # #Est ce que dw dans tmp pour etre a l aise et pas niquer la memoire ?
    # f = nxc.get_file('test.md')
    # pprint(f.fetch_file_content())
    # pprint(f.download())

    # # SYSTEMTAGS
    # pprint(nxc.get_systemtags().data)

    # # TAG x FILES
    # #Permet de taguer les notes selon la classe ? Deja sous fichier
    # pprint(nxc.create_systemtag('TAG_NAME').data)  # in fact useless , the tag will be created automatically


    # # and a user friendly one
    # #Voila on fait ca
    # f = nxc.get_file('/Nextcloud Manual.pdf')
    # f.add_tag(tag_name='TAG_NAME')
    # f.get_tags()
    # f.remove_tag(tag_name='TAG_NAME')
    # # to improve perfs you shall keep the tag ids fetched with get_systemtags

    # pprint(nxc.delete_systemtag('TAG_NAME').data)

