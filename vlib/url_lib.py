class urlsCrud:
    def __init__(self, model):
        self.model = model

    def BaseUrlUpdate(self, CountPageBack = 0):
        return self.GetBack(CountPageBack) + self.model.__name__ + '/update/'

    def BaseUrlDelete(self, CountPageBack = 0):
        return self.GetBack(CountPageBack) + self.model.__name__ + '/delete/'

    def BaseUrlList(self, CountPageBack = 0):
        return self.GetBack(CountPageBack) + self.model.__name__ + '/list'

    def BaseUrlInsert(self, CountPageBack = 0):
        return self.GetBack(CountPageBack) + self.model.__name__ + '/insert'

    def UrlInsert(self):
        return self.model.__name__ + '/insert'
  
    def UrlUpdate(self):
        return r'' + self.BaseUrlUpdate(-1) + '(?P<pk>\d+)/$'

    def UrlDelete(self):
        return  r'' + self.BaseUrlDelete(-1) +'(?P<pk>\d+)/$'

    def UrlList(self): 
        return r'' + self.BaseUrlList(-1)

    def GetBack(self, countBack):
        back = ''
        for a in range(0, countBack + 1):
            back = back + '../'
        return back

