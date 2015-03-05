import wx


class mTextCtrl(wx.TextCtrl):
    default_value = 'default'

    @property
    def value(self,):
        val = self.GetValue()
        if val == self.default_value:
            val = None
        else:
            try:
                val = float(val)
                if int(val) == val:
                    val = int(val)
            except:
                pass
        return val

    @value.setter
    def value(self, val):
        if val is None:
            val = self.default_value
        else:
            val = str(val)
        self.SetValue(val)


class mComboBox(wx.ComboBox, mTextCtrl):
    pass


class mCheckBox(wx.CheckBox,):

    @property
    def value(self,):
        return self.GetValue()

    @value.setter
    def value(self, val):
        self.SetValue(val)


class mChoice(wx.Choice,):

    @property
    def value(self,):
        val = self.Strings[self.GetCurrentSelection()]
        if hasattr(self, 'aliases'):
            for ky, lst in self.aliases.iteritems():
                if val in lst:
                    val = ky
        return val

    @value.setter
    def value(self, val):
        chcs = self.Strings
        if val.__class__ is not str:
            val = str(val)
        idx = None
        try:
            idx = chcs.index(val)
        except ValueError:
            if hasattr(self, 'aliases'):
                if val in self.aliases.keys():
                    idx = chcs.index(self.aliases[val][0])
        if idx is None:
            raise ValueError("'%s' is not a valid selection "
                             "for the '%s' Choice box." % (val, self.GetName()))
        else:
            self.SetSelection(idx)


class mChoiceBin(wx.Choice,):

    @property
    def value(self,):
        val = self.GetCurrentSelection()
        if hasattr(self, 'aliases'):
            val = self.aliases[val]
        return val

    @value.setter
    def value(self, val):
        if hasattr(self, 'aliases'):
            try:
                val = self.aliases.index(val)
            except:
                pass
        self.SetSelection(val)
