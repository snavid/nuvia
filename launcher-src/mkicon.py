from PIL import Image, ImageDraw
S=1024
img=Image.new('RGBA',(S,S),(0,0,0,0))
d=ImageDraw.Draw(img)
d.rounded_rectangle((0,0,S-1,S-1),radius=220,fill=(7,48,132,255))
def stroke(p1,p2,w,col):
    lay=Image.new('RGBA',(S,S),(0,0,0,0)); ld=ImageDraw.Draw(lay)
    ld.line([p1,p2],fill=col,width=w)
    for p in (p1,p2): ld.ellipse((p[0]-w/2,p[1]-w/2,p[0]+w/2,p[1]+w/2),fill=col)
    return lay
bottom=(450,760); w=170
img=Image.alpha_composite(img,stroke((280,440),bottom,w,(30,160,250,255)))
img=Image.alpha_composite(img,stroke(bottom,(760,250),w,(23,120,243,255)))
img.save('nuvia.png')
img.save('nuvia.ico',sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
img.resize((128,128),Image.LANCZOS).save('preview128.png')
