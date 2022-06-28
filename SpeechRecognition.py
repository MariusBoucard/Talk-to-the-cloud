from modulefinder import replacePackageMap
import resource
import easywebdav
from pprint import pprint
from termios import NCC
import nextcloud_client
from nextcloud import NextCloud
from tkinter.tix import ButtonBox
from typing_extensions import Self
import speech_recognition as sr
from PyQt5 import QtCore, QtGui,QtWidgets
from PyQt5.QtCore import Qt, QSettings,QUrl
from PyQt5.QtWidgets import QDialog, QApplication, QFileDialog, QMainWindow, QGraphicsScene,QGraphicsPixmapItem, QMessageBox,QListWidget, QLineEdit,QTextEdit
from PyQt5.uic import loadUi
import sys, os
import re
from datetime import datetime   
from PyQt5.QtMultimedia import QMultimedia, QMediaPlayer, QMediaContent
import subprocess
import platform
from Nextcloud_api import NCConnect as nc
from mdutils.mdutils import MdUtils
import urllib3
import nextcloud
from os.path import exists


#Par rapport a ca : automatiser la prise en charge de nouveaux fichier : stockage de la derniere date modifiée avec une sync nextcloud ?
#Process automatiquement, en fonction des 4/5 premiere seconde ou a posteriori pour les noms ?
#4/5 seconces peut etre bien car permet de set la langue pour classifier ensuite. Faire les tests sur les premiers mots dans toutes les langues pour choisir ensuite le bon interpreteur.

#Utiliser Q settings pour faire des trucs classés remanants et pouvant etre modifies -> path du fichier ; creation ou append a la fin

#Data pat classe : Langue, Nom, Fichier de sortie
#Choix du path vers les fichiers à sync et sur lesquels passer


class MainWindow(QMainWindow) :
    def __init__(self):
        self.settings = QSettings("Speech","settings")
        self.mediaPlayer = QMediaPlayer()
        super(MainWindow,self).__init__()
        self.pathui=resource_path("main.ui")
        loadUi(self.pathui,self)
        self.recognizer = sr.Recognizer()
        self.initconnections()
        self.AudioPath = []
        self.langue.addItems(["Français","Anglais"])
        if self.settings.value('tabSpeech') != None :
            self.tabSpeech = self.settings.value('tabSpeech')
        else : 
            self.tabSpeech = {}
        if self.settings.value('tabClass') != None :
            self.tabClass = self.settings.value('tabClass')
        else : 
            self.tabClass = {}

    def initconnections(self):
        self.Process.clicked.connect(self.process)
        self.aide.triggered.connect(self.help)
        self.sauve.triggered.connect(self.save)
        self.Quitter.triggered.connect(self.quit)
        self.Add.clicked.connect(self.loadsound)
        self.Remove.clicked.connect(self.remove)
        self.Up.clicked.connect(self.up)
        self.Down.clicked.connect(self.down)
        self.Purge.triggered.connect(self.purger)
        self.ProcessBruit.clicked.connect(self.processbruit)
        self.Play.setEnabled(False)
        self.classes.triggered.connect(self.gestclass)
        self.sortie_filenc.triggered.connect(self.ncsortie)
        # TODO
        self.fichiers_temporaires.triggered.connect(self.local_download)
        self.Slider.sliderMoved.connect(self.setPosition)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.Slider.sliderMoved.connect(self.setPosition)
        self.Preferences.triggered.connect(self.dialog)
        self.Sortielocale.triggered.connect(self.localset)
        self.Play.clicked.connect(self.play)
        self.listView.itemClicked.connect(self.initLecteur)

        self.syncbox.clicked.connect(self.syncnc)
        self.syncloc.triggered.connect(self.localfiles)

        self.SyncLocCB.clicked.connect(self.synclocs)

        self.Reinitialiser.triggered.connect(self.reinit)

    def ncsortie(self):
        d = Dialogncsortie(self)
        d.show()

    def reinit(self):
        self.settings.clear()
        mainWindow=MainWindow()
        widget=QtWidgets.QStackedWidget()
        widget.addWidget(mainWindow)
        widget.show()
    
    def local_download(self):
        fname=QFileDialog.getExistingDirectory(self,"Choisis un dossier de crevard, pour qu'on y enregistre tes sons de pute")
        self.settings.setValue("Local_Download",fname)
       

    def synclocs(self) :
        #Recuperation du path où aller chercher
        syncpath = self.settings.value("fichiers_locaux")
        print(syncpath)
        self.synced = self.settings.value("dejasyncloc")
        if self.synced == None :
            self.synced = []

        rappath=self.settings.value("rapport_path")
        rapliste = self.settings.value("rapport_list")
        if rapliste == None :
            rapliste = []
        if rappath == None :
            rappath = []
        j=0
        for root, dirs, files in os.walk(syncpath):
            #   print('Looking in:',root)
             for Files in files:
                chemfile=syncpath+Files
                if chemfile not in self.synced :
                    classe = self.autoprocess(chemfile)
                    print(chemfile+'processed')
                    self.synced.append(chemfile)
                    self.settings.setValue("dejasyncloc",self.synced)
                    rapliste.append(Files+" appartient à la classe : "+classe)
                    j=1
                    rappath.append(chemfile)
        if j==1: 
            if self.settings.value('ncsortiepath') != "":
                if self.settings.value('sortiemd') :
                    ##Todo
                    pass
                    #self.createmd()
                self.uploadbails()
            self.settings.setValue("rapport_path",rappath)
            self.settings.setValue("rapport_list",rapliste)
            d = Rapport(self)
            d.show()

    def localfiles(self):
        d = DialogFiles(self)
        d.show()

    def gestclass(self) :
        d = Dialogclass(self)
        d.show()

    def localset(self) :
         
        d = Dialogloc(self)
        d.show()
        

    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.Play.setText(
                    "Pause")
        else:
            self.Play.setText(
                    "Play")

    def positionChanged(self, position):
        self.Slider.setValue(position)
        self.Duree = self.mediaPlayer.duration()/1000
        Dm = int(self.Duree/60)
        Ds=round(self.Duree%60, 0)
        self.Time.setText(str(round(position/1000,0) )+"/"+str(Dm)+":"+str(Ds))
    
    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)
    
    def durationChanged(self, duration):
        self.Duree = self.mediaPlayer.duration()/1000
        Dm = int(self.Duree/60)
        Ds=round(self.Duree%60, 0)
        self.Slider.setRange(0, duration)
        self.Time.setText(str(duration)+"/"+str(Dm)+":"+str(Ds))

    def initLecteur(self) :
        self.Name= self.listView.currentItem().text()
        Path =""
        for element in self.AudioPath :
            gee=re.compile(".*/(.*)")
            gg = gee.search(element).group(1)
            if self.Name == gg :
                Path = element
                break
        
        if Path != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(Path)))
            self.Play.setEnabled(True)
        self.Taille = round(os.path.getsize(Path)/1000000,2)
    
        self.Modif = datetime.fromtimestamp(os.path.getatime(Path))
        self.Duree = self.mediaPlayer.duration()/1000
        Dm = int(self.Duree/60)
        Ds=round(self.Duree%60, 0)
        self.FileInfo.setText("Nom : "+self.Name+"\nTaille : "+str(self.Taille)+" Mo\nDernière modification : "+str(self.Modif)+"\nDurée : "+str(int(Dm))+" minutes, "+str(int(Ds))+" secondes")
        self.Time.setText("0/"+str(Dm)+":"+str(int(Ds)))

    def play(self):
        self.Duree = self.mediaPlayer.duration()/1000
        Dm = int(self.Duree/60)
        Ds=round(self.Duree%60, 0)
        self.FileInfo.setText("Nom : "+self.Name+"\nTaille : "+str(self.Taille)+" Mo\nDernière modification : "+str(self.Modif)+"\nDurée : "+str(int(Dm))+" minutes, "+str(int(Ds))+" secondes")
        self.Time.setText("0/"+str(int(Dm))+":"+str(int(Ds)))

        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def help(self):
        hono= QMessageBox()
        hono.setWindowTitle("Demander de l'aide")
        hono.setText("En cas de problème récurrent ou pour toute\n demande de modifications, la hotline\n est disponnible aux environs de l'heure\n du goûter.")
        hono.setIcon(QMessageBox.Information)
        hono.setStandardButtons(QMessageBox.Ok)
        hono.setInformativeText("Numéro de la Hotline : 0783811832\nAdresse mail pour réclamations : marius.boucard--bocciarelli@insa-rennes.fr\nattention néanmoins, en cas de plusieurs fichiers avec le même nom\nil risque d'y avoir des surprises")
        x = hono.exec_()

    def save(self):
        
        filename = QFileDialog.getSaveFileName(self, 'Sauvegarder le text produit', '', "All Files (*);; Fichier LibreOffice (*.odt);;Fichier txt (*.txt)", options=QFileDialog.DontUseNativeDialog)
        
        if filename[0] == '':
            return 0

        filename = filename[0]
        print(filename[1])
        sortie=open(filename,'w')
        sortie.write(self.TextOutput.toPlainText())
        sortie.close()
    
    def loadsound(self):
        
        fname=QFileDialog.getOpenFileName(self, 'Ouvrir un audio', './',"*.*")
        self.AudioPath.append(fname[0])
        gee=re.compile(".*/(.*)")
        self.listView.addItem(gee.search(fname[0]).group(1))
        self.Etat.setText("Prêt à être\ntranscrit.")
        # self.listView.addScrollBarWidget()

    def remove(self):
        aa= self.listView.currentItem().text()
        for element in self.AudioPath :
            gee=re.compile(".*/(.*)")
            gg = gee.search(element).group(1)
            if aa == gg :
                self.AudioPath.remove(element)
                self.listView.takeItem(self.listView.currentRow())
                break


    def process(self):
        try :
            langue= self.langue.currentText()
            setlangue =""
            if(langue == "Français") :
                setlangue = "fr-FR"
            elif(langue == "Anglais") :
                setlangue = "en-EN"
            gee=re.compile(".*/(.*)")

            for i in range(0,self.listView.count()) :
                self.name = self.listView.item(i).text()
                
                for element in self.AudioPath :
                    gg = gee.search(element).group(1)
                   
                    if self.name == gg : 
                        self.chgt(i+1)
                        
                        af = sr.AudioFile(element)
                        with af as source:
                           audio = self.recognizer.record(source)
                        reconnu = self.recognizer.recognize_google(audio,language=setlangue)
                        self.TextOutput.appendPlainText(reconnu+"\n")
            self.Etat.setText("Travail terminé.")
            
        except  :
           err = ""
           hono= QMessageBox()
           hono.setWindowTitle("Une erreur s'est produite")
           hono.setText("Il y a eu un problème pendant la conversion des audios : \n audio fautif : "+self.name)
           hono.setIcon(QMessageBox.Critical)
           hono.setStandardButtons(QMessageBox.Ok)
           hono.setInformativeText("Le message d'erreur envoyé : \n"+err)
           x = hono.exec_()

    def chgt(self,i) :
        a = str(self.listView.count())
        self.Etat.setText("Travail sur \nl'enregistrement\n"+str(i)+"/"+a)
        self.Etat.repaint()


    def processbruit(self):
        try :
            langue= self.langue.currentText()
            setlangue =""
            if(langue == "Français") :
                setlangue = "fr-FR"
            elif(langue == "Anglais") :
                setlangue = "en-EN"
            gee=re.compile(".*/(.*)")

            for i in range(0,self.listView.count()) :
                self.name = self.listView.item(i).text()
                for element in self.AudioPath :
                    gg = gee.search(element).group(1)
                    if self.name == gg : 
                        self.chgt(i+1)
                        af = sr.AudioFile(element)
                        with af as source:
                           self.recognizer.adjust_for_ambient_noise(source)
                           audio = self.recognizer.record(source)
                        reconnu = self.recognizer.recognize_google(audio,language=setlangue)
                        self.TextOutput.appendPlainText(reconnu+"\n")
            self.Etat.setText("Travail terminé.")

         
        except :
           err = ""
           hono= QMessageBox()
           hono.setWindowTitle("Une erreur s'est produite")
           hono.setText("Il y a eu un problème pendant la conversion des audios : \n audio fautif : "+self.name)
           hono.setIcon(QMessageBox.Critical)
           hono.setStandardButtons(QMessageBox.Ok)
           hono.setInformativeText("Le message d'erreur envoyé : \n"+err)
           x = hono.exec_()

    def purger(self):
        self.AudioPath.clear()
        self.listView.clear()



    def up(self):
        
        if self.listView.currentRow() == 0 :
           return
        row=self.listView.currentRow()
        name = self.listView.currentItem().text()
        self.listView.takeItem(self.listView.currentRow())
        self.listView.insertItem(row-1,name)

    def down(self):
        
        aa= int(self.listView.count())
        if self.listView.currentRow() == aa-1 :
               return

        row=self.listView.currentRow()
        name = self.listView.currentItem().text()
        self.listView.takeItem(self.listView.currentRow())
        self.listView.insertItem(row+1,name)

    
    def quit(self) :
        quit()
    
    def dialog(self): 
        d = Dialog(self)
        d.show()

    def syncnc(self) :
        self.wd=resource_path(os.getcwd())
        print(self.settings.value("ncurl"))
        print(self.settings.value("ncuser"))
        print(self.settings.value("ncmdp"))

        next =nc(self.settings.value("ncurl"),self.settings.value("ncuser"),self.settings.value("ncmdp"))
        
        self.synced = self.settings.value("dejasync")
        rappath=self.settings.value("rapport_path")
        if rappath == None :
            rappath= []
        rapliste = self.settings.value("rapport_list")
        if rapliste == None :
            rapliste =[]
        if self.synced == None :
            self.synced = []
        print(self.settings.value("ncpath"))
        next.pathFile(self.settings.value("ncpath"))
        print(next.getPath())
        self.listerecup = next.recuperation()
   
        j=0
        for f in self.listerecup : 
             if (not f in self.synced) & (not f.isdir()) :
                listepat = re.split("/",next.path)
                stri = re.sub("'}\)","",str(f))
                listefile=re.split("/",stri)
                a=0
                fileadr =""
                for part in listefile :
                    if part == listepat[1] or a==1 :
                        a=1
                        fileadr+="/"+part
                j=1
                filename = listefile[len(listefile)-1]
                a = self.settings.value("Local_Download")
                if a != None :
                    next.downloadpath(a,fileadr)
                    os.chdir(self.wd)
                    print(a+filename)
                    classe = self.autoprocess( a+"/"+filename)
                    rappath.append(a+"/"+filename)
                else:    
                    print("\n\n\n couilles\n\n")
                    next.downloadtmp(fileadr)
                    os.chdir(self.wd)
                    classe = self.autoprocess("/tmp/"+filename)
                    rappath.append('/tmp/'+filename)
                print(filename+'processed')
                self.synced.append(f)
                self.settings.setValue("dejasync",self.synced)
                rapliste.append(filename+" appartient à la classe : "+classe)
                
        #if j==1:
        self.settings.setValue("rapport_path",rappath)
        self.settings.setValue("rapport_list",rapliste)
        if self.settings.value('ncsortiepath') != "":
            if self.settings.value('sortiemd') :
               pass
                # self.createmd(rappath,rapliste)
           # self.uploadbails()
        
        d = Rapport(self,rappath,rapliste)
        d.show()
        

    def createmd(self,pathfiles,listefile) :
        file = self.settings.value('ncsortiepath')+"/"+"Readme.md"
        mdFile = MdUtils(file_name=file,title='Rapport de traitement')
        mdFile.new_header(level=1, title='Liste des fichiers audios ayant été lu sur cette session :')
        print(len(listefile))
        print(listefile)
        print(pathfiles)
        for file in range(len(listefile)-1) :
            mdFile.new_line(listefile[file]+" et est stocké en : "+pathfiles[file], bold_italics_code='cib', align='center')
        # mdFile.new_list(listefile)
        # link = self.settings.value("rapport_path")
        # mdFile.write("\n  - Reference link: " + mdFile.new_reference_link(link=link, text='ouverture du chemin du rapport', reference_tag='1'))
        mdFile.create_md_file()

    def uploadbails(self) :
        upplace = self.settings.value("ncsortiepath")
        hereplace = self.settings.value("sortiepath")
        try :
            next =nc(self.settings.value("ncurl"),self.settings.value("ncuser"),self.settings.value("ncmdp"))
        except :
            print("are you sure to have entered right creditentials to nextcloud")
            return
        next.pathFile(upplace)
        for root, dirs, files in os.walk(hereplace):
            for Files in files:
                print(hereplace+Files)
                
                next.upload(hereplace+Files, upplace+Files)
            
        print("tout bien upload")




        # TODO

    def autoprocess(self,file) :
        try :
            #Selection de la langue et de la classe ?

            print("processing de : "+file)
            af = sr.AudioFile(file)
            
            self.tabclass = self.settings.value("tabclasse")
            if self.tabclass == None :
                self.tabclass = {'Becane' : 'fr-FR',
                                'Projet' : 'fr-FR'}
            self.sortiepath = self.settings.value("sortiepath")

            print(self.tabClass)
            with af as source:
                audio = self.recognizer.record(source, duration =2)
                audio2 = self.recognizer.record(source, offset=2)

                try :
                    classeen = self.recognizer.recognize_google(audio,language = "en-US")
                    classeen = classeen.upper()
                except :
                    print('on a pas trouvé de anglais')
                    classeen =""
                try :
                    classefr = self.recognizer.recognize_google(audio,language = "fr-FR")
                    classefr = classefr.upper()
                except:
                    print('on a pas trouvé de français')
                    classefr=""
                a=0

                print('classeen '+classeen+"\nclassefr "+classefr)
                print(self.tabclass)
                for classe in self.tabclass.keys():
                    kk= classe.upper()
                    if kk in classeen :
                        try :
                            text = self.recognizer.recognize_google(audio2,language = self.tabclass[classe])
                            self.tabSpeech[file] = text
                            self.settings.setValue("tabSpeech",self.tabSpeech)
                            self.tabClass[file] = kk
                            self.settings.setValue("tabClass",self.tabClass)
                            # f = open(self.sortiepath+classe,"a")
                            # f.write("\n"+text)
                            # print("oklm")
                            # f.close()
                            a=1
                            return classeen
                        except : 
                            print('le reuf a r compris')
                            self.tabSpeech[file] = "no txt found"
                            self.tabClass[file] = kk
                            self.settings.setValue("tabClass",self.tabClass)
                            self.settings.setValue("tabSpeech",self.tabSpeech)
                            a=1
                            return "erreur avec : "+classeen

                        break;
                    if kk in classefr : 
                        try :
                            text = self.recognizer.recognize_google(audio2,language = self.tabclass[classe])
                            self.tabSpeech[file] = text
                            self.tabClass[file] = kk
                            self.settings.setValue("tabSpeech",self.tabSpeech)
                            self.settings.setValue("tabClass",self.tabClass)
                            a=1
                            # f = open(self.sortiepath+classe,"a")
                            # f.write("\n"+text)
                            # print("oklm")
                            # f.close()
                            return classefr
                        except : 
                            print('le reuf a r compris')
                            self.tabSpeech[file] = "no txt found"
                            self.tabClass[file] = kk
                            self.settings.setValue("tabClass",self.tabClass)
                            self.settings.setValue("tabSpeech",self.tabSpeech)
                            a=1
                            return "erreur avec : "+classefr
                        a=1
                        break;
                
                if a==0:
                    print("rien a ete trouvé") 
                    try :
                        text = self.recognizer.recognize_google(audio,language="fr-FR")
                        text+= self.recognizer.recognize_google(audio2,language="fr-FR")
                        self.tabSpeech[file] = text
                        self.tabClass[file] = "no Class found"
                        self.settings.setValue("tabClass",self.tabClass)
                        self.settings.setValue("tabSpeech",self.tabSpeech)
                        # f = open(self.sortiepath+"no class","a")
                        # f.write("\n"+text)
                        # print("oklm")
                        # f.close()
                        return 'no class'
                    except :
                        print("c'est la d")
                        self.tabSpeech[file]="No text found"
                        self.tabClass[file] = "no Class found and error"
                        self.settings.setValue("tabSpeech",self.tabSpeech)
                        self.settings.setValue("tabClass",self.tabClass)
                        return "erreur avec : no class"

            
            #self.Etat.setText("Travail terminé.")
            
        except  :
           err = ""
           hono= QMessageBox()
           hono.setWindowTitle("Une erreur s'est produite")
           hono.setText("Il y a eu un problème pendant la conversion des audios : \n audio fautif : "+file)
           hono.setIcon(QMessageBox.Critical)
           hono.setStandardButtons(QMessageBox.Ok)
           hono.setInformativeText("Le message d'erreur envoyé : \n"+err)
           x = hono.exec_()
           return "erreur totale"
       

def resource_path(relative_path):
    
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

      
class Dialog(QDialog):
    def __init__(self, parent=None):

        QDialog.__init__(self, parent)
        self.pathui=resource_path("dialognc.ui")
        loadUi(self.pathui,self)
        self.settings = QSettings("Speech","settings")
        if self.settings.value("ncpath") != None :
            self.ncpath.setText(self.settings.value("ncpath"))
        if self.settings.value("ncuser") != None :
            self.ncnomutilisateur.setText(self.settings.value("ncuser"))
        if self.settings.value("ncurl") != None :
            self.ncadresse.setText(self.settings.value("ncurl"))

        self.buttonBox.accepted.connect(self.accept)
       


    def accept(self) :
        self.settings.setValue("ncpath",self.ncpath.text())
        self.settings.setValue("ncuser",self.ncnomutilisateur.text())
        if self.ncmdp.text() != None : 
            self.settings.setValue("ncmdp",self.ncmdp.text())
        self.settings.setValue("ncurl",self.ncadresse.text())
        self.close()


class Dialogloc(QDialog):
    def __init__(self, parent=None):

        QDialog.__init__(self, parent)
        self.pathui=resource_path("dialogsortie.ui")
        loadUi(self.pathui,self)
        self.settings = QSettings("Speech","settings")
        if self.settings.value("sortiepath") != None :
            self.SortiePath.setText(self.settings.value("sortiepath"))
        self.buttonBox.accepted.connect(self.accept)
        self.openDir.clicked.connect(self.chgout)

    def chgout(self) :
            fname=QFileDialog.getExistingDirectory(self,"Choisis un dossier de crevard")
            self.SortiePath.setText(fname+"/")

        
       


    def accept(self) :
        self.settings.setValue("sortiepath",self.SortiePath.text())
        self.close()
        


class Dialogclass(QDialog):
    def __init__(self, parent=None):

        QDialog.__init__(self, parent)
        self.pathui=resource_path("classesgest.ui")
        loadUi(self.pathui,self)
        self.settings = QSettings("Speech","settings")
        
        self.dico = {"default":"en-US"}
        
        if self.settings.value("tabclasse") != None :
            self.dico = self.settings.value("tabclasse")
            self.List.addItems(self.dico)
        self.buttonBox.accepted.connect(self.accept)
        self.add.clicked.connect(self.Add)
        self.Supprimer.clicked.connect(self.remove)
        self.Langue.addItems(["en-US","fr-FR"])

    def remove(self):
        self.dico.pop(self.List.currentItem().text())
        self.List.clear()
        self.List.addItems(self.dico.keys())

    def Add(self) :
        self.dico[self.NomClasse.text()] = self.Langue.currentText()
        self.List.addItem(self.NomClasse.text())

        
       

    def accept(self) :
        self.settings.setValue("tabclasse",self.dico)
        self.close()

class DialogFiles(QDialog):
    def __init__(self, parent=None):

        QDialog.__init__(self, parent)
        self.pathui=resource_path("dialogloc.ui")
        loadUi(self.pathui,self)
        self.settings = QSettings("Speech","settings")
        
        if self.settings.value("fichiers_locaux") != None :
            self.Pathdoss.setText(self.settings.value("fichiers_locaux"))

        self.buttonBox.accepted.connect(self.accept)
        self.recherche.clicked.connect(self.browse)
       
  

    def browse(self) :
        fname=QFileDialog.getExistingDirectory(self,"Choisis un dossier de crevard")
        self.Pathdoss.setText(fname+"/")


    def accept(self) :
        self.settings.setValue("fichiers_locaux",self.Pathdoss.text())
        self.close()


class Dialogncsortie(QDialog):
    def __init__(self, parent=None):

        QDialog.__init__(self, parent)
        self.pathui=resource_path("sortnc.ui")
        loadUi(self.pathui,self)
        self.settings = QSettings("Speech","settings")
        
        if self.settings.value("ncsortiepath") != None :
            self.Pathnc.setText(self.settings.value("ncsortiepath"))

        self.buttonBox.accepted.connect(self.accept)
        self.checkBox.setCheckState(bool(self.settings.value("sortiemd")))
        
       
  

    def browse(self) :
        fname=QFileDialog.getExistingDirectory(self,"Choisis un dossier de crevard")
        self.Pathdoss.setText(fname+"/")


    def accept(self) :
        self.settings.setValue("ncsortiepath",self.Pathnc.text())
        if self.checkBox.isChecked() :
            self.settings.setValue('sortiemd',True)
        else :
            self.settings.setValue('sortiemd',False)
        self.close()

class Rapport(QDialog):
    def __init__(self, parent=None, path=None,file=None):

        QDialog.__init__(self, parent)
        self.pathui=resource_path("rapport.ui")
        loadUi(self.pathui,self)
        self.settings = QSettings("Speech","settings")
        print(self.settings.value("rapport_list"))
        self.dicclasse =self.settings.value('tabClass')
        self.dicText= self.settings.value('tabSpeech')
        self.sortiepath = self.settings.value("sortiepath")
   
        self.pathlist = path
        self.filelist= file
        if self.filelist != None :
             self.list.addItems(self.filelist)
        self.Path = ""
        self.Play.clicked.connect(self.play)
        self.mediaPlayer = QMediaPlayer()
        self.Slider.sliderMoved.connect(self.setPosition)
        self.mediaPlayer.stateChanged.connect(self.mediaStateChanged)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.Sortie.clicked.connect(self.opendir)
        self.list.itemClicked.connect(self.initLecteur)
        self.Validation.clicked.connect(self.validation)
        self.Validaudio.clicked.connect(self.validUnit)
        self.recupall()


        print("\n\n"+str(self.dicclasse))
        #Download everybails
    def recupall(self):

        upplace = self.settings.value("ncsortiepath")
        hereplace = self.settings.value("sortiepath")
        try :
            next =nc(self.settings.value("ncurl"),self.settings.value("ncuser"),self.settings.value("ncmdp"))
        except :
            print("\n\nARE YOU SURE TO HAVE SET NEXTCLOUD CREDITENTIALS ??\n\n")
            return
        a =next.getFileList(upplace)

        for file in a:
            if (not file.isdir()) :
                
                stri = re.sub("'}\)","",str(file))
                listefile=re.split("/",stri)
                filename =listefile[len(listefile)-1]
                filepathnc = upplace+'/'+filename
                if exists(hereplace+filename):
                    os.remove(hereplace+filename)
                if filepathnc != None :
                    print("filepath up "+filepathnc)
                    try :
                        next.downloadpath(hereplace,upplace+"/"+filename)
                    except : 
                        print('ca a chie dans la colle')
                print(filename+" downloaded in "+hereplace)
        
        

    def validUnit(self):
        self.dicclasse[self.Path] = self.LineClasse.text()
        
        self.dicText[self.Path] = self.TextAudio.toPlainText()
        self.settings.setValue("tabClasse",self.dicclasse)
        self.settings.setValue("tabSpeech",self.dicText)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)


    def positionChanged(self, position):
        self.Slider.setValue(position)

    def validation(self) :
        self.ecrirelesbails()
        self.deadca()
        self.settings.setValue("rapport_list",[])
        self.settings.setValue("rapport_path",[])
        self.settings.setValue('tabClass',{})
        self.settings.setValue('tabSpeech',{})
        self.uploadbails()
        self.close()

    def deadca(self):
        a =self.settings.value("Local_Download")
        self.wd=resource_path(os.getcwd())
        pathlist = self.settings.value("rapport_path")
        if a != None :
            os.chdir(a)
            for path in pathlist :
                os.remove(path) 
            os.chdir(self.wd)



    def ecrirelesbails(self):
        
        for speech in self.dicText.keys():
            # spee = re.split("/",speech)
            # speech = spee[-1]
            file = open(self.sortiepath+"/"+self.dicclasse[speech]+".txt","a")
            file.write("\n\n"+self.dicText[speech])
            file.close()

    def opendir(self) :
    
         if platform.system() == "Windows":
          os.startfile(self.DirOut)
         elif platform.system() == "Darwin":
            subprocess.Popen(["open", self.settings.value("sortiepath")])
         else:
            subprocess.Popen(["xdg-open", self.settings.value("sortiepath")])
         pass
    
    def mediaStateChanged(self, state):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.Play.setText(
                    "Pause")
        else:
            self.Play.setText(
                    "Play")

    def durationChanged(self, duration):
        self.Slider.setRange(0, duration)
       
    
    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
                self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def initLecteur(self) :
        self.id= self.list.currentRow()
        
        self.Path = self.pathlist[int(self.id)]
        self.TextAudio.setText(self.dicText[self.Path])
        self.LineClasse.setText(self.dicclasse[self.Path])
        
        if self.Path != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(self.Path)))
            self.Play.setEnabled(True)
    
    def uploadbails(self) :
        upplace = self.settings.value("ncsortiepath")
        hereplace = self.settings.value("sortiepath")
        try :
            next =nc(self.settings.value("ncurl"),self.settings.value("ncuser"),self.settings.value("ncmdp"))
        except :
            print("are you sure to have put the great values for your nc account ?")
            return
        next.pathFile(upplace)
        for root, dirs, files in os.walk(hereplace):
            for Files in files:
                print(hereplace+Files)
                
                next.upload(hereplace+Files, upplace+Files)
            
        print("bien upload")
    


if __name__ == '__main__':
# rECUPERATION DES ARGUMENTS AU LANCÉ
# Gestion de comment ca c est passé tout ca 
    app=QApplication(sys.argv)
    mainWindow=MainWindow()
    widget=QtWidgets.QStackedWidget()
    widget.addWidget(mainWindow)
   
    try :
        if sys.argv[1] == "sync" :
            print("couillasses")
            mainWindow.syncnc()
            mainWindow.synclocs()
        else :
            
            widget.show()
            sys.exit(app.exec_())
    except :
            
            widget.show()
            sys.exit(app.exec_())