'''
Created on Nov 13, 2009

@author: kbandla
'''

from sgmllib import SGMLParser
import re

class PageParser(SGMLParser):
    def reset(self):                              
        SGMLParser.reset(self)
        self.js_body = []
        self.vbs_body = []
        self.js_script_srcs = []
        self.vbs_script_srcs = []
        self.js_inScript = False
        self.vbs_inScript = False
        self.hrefs = []
        self.iframes = []
        self.imgs = []
        self.frames = []
        self.objects = []
        self.clsids = []
        self.onload = '\n'
        #self.js_body.append(self.a.js_body)

    def start_body(self, attrs):
        for k, v in attrs:
            if k.lower() == 'onload':
                if v not in self.onload:
                    v = re.sub('JavaScript:', '', v, re.IGNORECASE)
                    v = re.sub('return', '', v, re.IGNORECASE)
                    self.onload += ' %s' % v

    def end_body(self): 
        pass

    def start_ie(self, attrs):
        for k, v in attrs:
            if k.lower() == 'id':
                self.onload += '%s = new ClientCaps();' % v

    def end_ie(self):
        pass

    def start_input(self, attrs):
        onload = False
        lang = False
        for k, v in attrs:
            if k.lower() == 'onclick':
                if v not in self.onload: self.onload += v
            if k.lower() == 'language':
                VBS_TYPES = [ x.lower() for x in ('VBS', 'VBScript', 'VisualBasic') ]
                if v.lower() in VBS_TYPES: lang = 'VB'
                else: lang = 'JS'
            if lang and onload:
                if lang == 'JS': self.onload += '\n%s;' % onload
                if lang == 'VB': self.onload += '\n%s' % onload

    def end_input(self):
        pass

    def start_iframe(self, attrs):
        for k, v in attrs:
            if k.lower() == 'src':
                if v not in self.iframes: self.iframes.append(v)
    
    def end_iframe(self):
        pass
    
    def start_frame(self, attrs):
        for k, v in attrs:
            if k.lower() == 'src':
                if v not in self.frames: self.frames.append(v)

    def end_frame(self):
        pass
    
    def start_a(self, attrs):
        for k, v in attrs:
            if k.lower() == 'href':
                if v not in self.hrefs: self.hrefs.append(v)
                if k.lower() == 'onclick':
                    if v not in self.onload: self.onload += '%s;' % v
                
    def end_a(self):
        pass

    def start_meta(self, attrs):
        for k, v in attrs:
            if k.lower() == 'content' and 'url=' in v.lower():
                url = v.split(';')
                for u in url:
                    if u.lower().startswith('url='):
                        url = re.sub('URL=', '', u, re.IGNORECASE)
                        url = url.replace('"', '')
                        if url not in self.hrefs: self.hrefs.append(url)

    def end_meta(self):
        pass

    def start_img(self, attrs):
        for k, v in attrs:
            if k.lower() == 'src':
                if v not in self.imgs: self.imgs.append(v)

    def end_img(self):
        pass

    def start_script(self, attrs):                
        # script defaults to JavaScript ...
        self.js_inScript = True

        script_types =  [ x.lower() for x in [ v for k, v in attrs ] ]
        # handle VBS explicitly
        VBS_TYPES = [ x.lower() for x in ('VBS', 'VBScript', 'VisualBasic') ]
        for t in VBS_TYPES:
            if t in script_types:
                self.vbs_inScript = True
                self.js_inScript = False
        # do we have a separate location for the script?
        for k, v in attrs:
            if k.lower() == 'src':
                if self.js_inScript:
                    if v not in self.js_script_srcs: self.js_script_srcs.append(v)
                elif self.vbs_inScript:
                    if v not in self.vbs_script_srcs: self.vbs_script_srcs.append(v)
        # force a newline before the next script body
        self.js_body.append(';\n')
        self.vbs_body.append('\n')
        # when in a script body, set literal to be True. this is because
        # SGML parsers will intercept things like foo<bar and '<v:rect' 
        # and think it's a tag, munging up the content
        self.literal = 1
    
    def end_script(self):
        if self.js_inScript:
            if not self.js_body[-1].endswith(';'):
                self.js_body.append(';')
        self.vbs_inScript = False
        self.js_inScript = False
        self.literal = 0

    def start_object(self, attrs):
        for k, v in attrs:
            if k.lower() == 'data':
                if v not in self.objects: self.objects.append(v)
            # handle ActiveX classid definitions, bring in javascript mock objects
            if k.lower() == 'classid':
                if v.upper() not in self.clsids:
                    v = v.upper().replace('CLSID:', '')
                    v = v.replace('{', '').replace('}', '')
                    self.clsids.append(v)
                    obj_id = False
                    for i, j in attrs:
                        if i == 'id': obj_id = j
            if i == 'name': 
                obj_id = j
                obj = self.a.get_obj_by_clsid(v)
                if not obj: 
                    print 'UNKNOWN CLSID: %s' % v
                    continue                    # we don't know about it
                if obj_id:
                    code = '\n%s = new %s();' % (obj_id, obj.classname)
                    self.js_body.append(code) 
                    break

    def end_object(self):
        pass            

    def characters(self, content):
        self.text = self.text + content

    def handle_data(self, text):           
        if self.js_inScript: self.js_body.append(text)
        if self.vbs_inScript: self.vbs_body.append(text)
