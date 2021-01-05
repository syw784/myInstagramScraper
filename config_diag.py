from PyQt5 import QtWidgets, uic
import sys

class Query_URL_Ui(QtWidgets.QDialog):


    def click_ok(self):
        self.param['usr_name']          = self.usr_text.text()
        self.param['pswd']              = self.pswd_text.text()
        self.param["query_format"]      = self.query_text.text()
        self.param["path"]              = self.savepath_text.text()
        #self.param["headers"]            = self.header_text.text()

    # def click_cancel(self):
    #     print('poo')
    
    def __init__(self, param):
        super(Query_URL_Ui, self).__init__()
        uic.loadUi('text_diag.ui', self)
#        self. = self.findChild(QtWidgets., '') # Find the button
        self.param = param
        self.buttons = self.findChild(QtWidgets.QDialogButtonBox, 'buttonBox') # Find the button
        self.query_text = self.findChild(QtWidgets.QLineEdit, 'query_text') # Find the button
        self.usr_text = self.findChild(QtWidgets.QLineEdit, 'usr_name_text') # Find the button
        self.pswd_text = self.findChild(QtWidgets.QLineEdit, 'pswd_text') # Find the button
        #self.header_text = self.findChild(QtWidgets.QLineEdit, 'header_text') # Find the button
        self.savepath_text = self.findChild(QtWidgets.QLineEdit, 'savepath_text') # Find the button
        self.query_text.setText(param["query_format"])
        self.usr_text.setText(param['usr_name'])
        self.pswd_text.setText(param['pswd'])
        self.savepath_text.setText(param['path'])
        #self.header_text.setText(param['headers'])
        self.buttons.accepted.connect(self.click_ok)
        # self.buttons.rejected.connect(self.click_cancel)
        self.show()
        #self.setFixedSize()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    wind = Query_URL_Ui([])
    app.exec_()