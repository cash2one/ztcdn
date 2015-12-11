#!/usr/bin/env python
# coding: UTF-8
import MySQLdb
class CName(object):
   def __init__(self):
      self.conn=MySQLdb.connect(host='172.30.250.186',user='dns',passwd='Kqyygywcw1',port=3306)
      self.cur=self.conn.cursor(MySQLdb.cursors.DictCursor)
      self.conn2=MySQLdb.connect(host='172.30.250.149',user='cloud_cdn',passwd='Cloud_Cdn113322',port=3306)
      self.cur2=self.conn2.cursor(MySQLdb.cursors.DictCursor)
   def get_zone(self,domain):
      self.cur.execute('select id from dns.domain where name=%s;' , domain)
      _domainid=self.cur.fetchone()
      _domainID=_domainid['id']

      self.cur.execute('select id from dns.domain_zone where domain_id=%s;' , _domainID)
      _domainzone_ids=self.cur.fetchall()
      _domainzone_idl=[]
      for _domainzone_id in _domainzone_ids:
         _domainzone_idl.append(str(_domainzone_id['id']))
      #self.cur.close()
      #self.conn.close()
      return _domainzone_idl
   def get_domain_cname(self,distid):
      _distid=distid
      self.cur2.execute('select id,domain_type,domain_name from cloud_cdn.cdn_manage_domain where domain_id=%s;' , _distid)
      _domain_v=self.cur2.fetchone()
      _domain_v_id=_domain_v["id"]
      _domain_v_type=_domain_v["domain_type"]
      _domain_v_name=_domain_v["domain_name"]
      if _domain_v_type == "web":
         sp_domain_type="dl_api"
      elif _domain_v_type == "download":
         sp_domain_type="ws_api"
      self.cur2.execute('select domain_cname from cloud_cdn.cdn_manage_sp where domain_table_id=%s and sp_domain_type="%s";' % (_domain_v_id, sp_domain_type))
      _sp_sql=self.cur2.fetchone()
      _sp_sql["domain_name"] = _domain_v_name
      return _sp_sql

   #def insert_cname(self,jrdns,distid):
   def insert_cname(self,distid):
      sp_sql = self.get_domain_cname(distid)
      _jrdns=sp_sql["domain_name"]
      _cdndns=sp_sql["domain_cname"]
      _zone_list=self.get_zone('giantcdn.com')
      self.cur.execute('delete from dns.node where name="%s"' % (_jrdns))
      for _zone in _zone_list:
          self.cur.execute('insert into dns.node(fix,type,ip,domain_id,name) values("IN","CNAME","%s","%s","%s")' % (_cdndns+".", _zone, _jrdns))
      self.conn.commit()
      self.cur.close()
      self.conn.close()

   def del_cname(self,distid):
      sp_sql = self.get_domain_cname(distid)
      _jrdns=sp_sql["domain_name"]
      self.cur.execute('delete from dns.node where name=%s' , (_jrdns))
      self.conn.commit()
      self.cur.close()
      self.conn.close()

if __name__ == '__main__':
    a=CName()
    #print a.del_cname('21bba682-973a-11e5-bbf0-fa163ed3937f')
    #print a.insert_cname('21bba682-973a-11e5-bbf0-fa163ed3937f')
