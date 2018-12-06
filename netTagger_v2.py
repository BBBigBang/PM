#!/usr/bin/env python
# coding=utf-8
import logging;
import socket;
from dlut import asyncore_epoll;
from dlut import ner_v2;
from dlut import relation;

import json;
import codecs;
#from ssplit.ssplit_token import Tokenize;
#two class about event loop
class TaggerServer(asyncore_epoll.dispatcher):
    #{{{
    """
    Receives connections and establishes handlers for each client.
    """
    
    def __init__(self, address,tagger_fn=None):
        self.logger = logging.getLogger('TaggerServer')
        asyncore_epoll.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.bind(address)
        self.address = self.socket.getsockname()
        self.logger.debug('binding to %s', self.address)
        self.listen(5)
        self.tagger_fn=tagger_fn;
        return

    def handle_accept(self):
        # Called when a client connects to our socket
        client_info = self.accept()
        self.logger.debug('accept client: %s', client_info[1])
        TaggerHandler(sock=client_info[0],tagger_fn=self.tagger_fn);
        return
    
    def handle_close(self):
        self.logger.debug('TaggerServer close')
        self.close()
        return
#}}}
class TaggerHandler(asyncore_epoll.dispatcher):
    #{{{
    """
    Handles tagger request from a client.
    """
    
    def __init__(self, sock, tagger_fn=None,chunk_size=2048):
    #{{{
        self.chunk_size = chunk_size
        self.logger = logging.getLogger('TaggerHandler%s' % str(sock.getsockname()))
        asyncore_epoll.dispatcher.__init__(self, sock=sock)
        self.revData=[];
        self.sendData=[];
        self.revComplete=True;
        self.sendComplete=True;
        self.tagger_fn=tagger_fn;
        return
    #}}}
    def writable(self):
    #{{{
        """
        We want to write if we have tagged data.
        """
        response = bool(self.sendData)
        #self.logger.debug('writable() -> %s', response)
        return response
    #}}}
    def handle_write(self):
    #{{{
        """
        Write the first element of sendData to peer.
        the writed data has two format:
            length+space+data:      a new tagger result.
            remaining_data:         the remaining data.
        """
        if not self.sendData:
            return;
        data = self.sendData[0]
        if self.sendComplete:
            #last send has completed, 
            #so this time is a new tagger result. 
            sent=self.send(str(len(data))+' '+data);
        else:
            #last send haven't completed
            sent=self.send(data);
        self.logger.debug('send:{}'.format(sent));
        #self.logger.debug('len(data)={}'.format(len(data)));
        if sent < len(data):
            remaining = data[sent:]
            self.sendData[0]=remaining;
            self.sendComplete=False;
        else:
            #send data completed 
            self.sendData.pop();
            self.sendComplete=True;
        #self.logger.debug('handle_write() -> (%d) "%s"', sent, data[:sent])
    #}}}
    def handle_read(self):
    #{{{
        """
        Read an incoming message from the client. 
        The sended data has two format:
            length+space+data:      a new tagger request  
            remaining_data:         this data should be append to the last one
        """
        try:
            data= self.recv(self.chunk_size)
        except socket.error.EAGIN or socket.error.EWOULDBLOCK:
            #wait for available
            return;
        if not data:
            #empty string, the peer has closed, so we also closes
            return;
        self.revData.append(data);
        i=0;
        #find the first space 
        for elem in self.revData:
            firstSpacePos=elem.find(' ');
            if firstSpacePos!=-1:
                break;
            i+=1;
        if firstSpacePos!=-1:
            #get length 
            length=''.join(self.revData[:i]);
            length+=self.revData[i][:firstSpacePos];
            try:
                length=int(length);
            except ValueError:
                #client don't follow the send format we mentioned
                #so close the client
                self.revData=[];
                self.sendData=[];
                self.handle_close();
                return;
            count=-firstSpacePos-1;
            for j in range(i,len(self.revData)):
                count+=len(self.revData[j]);
                if count>=length:
                    completeData=''.join(self.revData[i:j+1]);
                    completeData=completeData[firstSpacePos+1:length+firstSpacePos+1];
                    #pop complete data 
                    for m in range(j):
                        self.revData.pop(0);
                    self.revData[0]=self.revData[0][len(self.revData[0])-(count-length):]
                    #use complete data to tagger 
                    self.tagger(completeData);
                    break;
            if count< length:
                #last data still not complete, wait to rev again
                return;
        #self.logger.debug('handle_read() -> (%d) "%s"', len(data), data)
    #}}}
    def handle_close(self):
        self.logger.debug('handle_close()')
        self.close()
    
    def tagger(self,data):
        """
        do tagger 
        data is type+space+real-data
        """
        #self.logger.debug('tagger()--'+data)
        """
        if data[:pos]=='@Text@':
            flag=True;
        else:
            flag=False;

        """
        if self.tagger_fn is None:
            self.sendData.append(data.decode('utf-8'));
        else:
            #self.sendData.append(self.tagger_fn(realData.decode('utf-8'),flag).encode('utf-8'));
            self.sendData.append(self.tagger_fn(data));
       # self.logger.debug('tagger...,len(self.sendData)={}'.format(len(self.sendData)));
#}}}

if __name__ =='__main__':
    import os;
    #log 
    logging.basicConfig(level=logging.DEBUG,
                        format='%(name)s:%(message)s',);
    logger=logging.getLogger('netTagger:');
    print "PID:",os.getpid();

    #load source
    #{{{
    #load machine leanring tagger model 
    print "Loading model..."
    modelPath='./dlut/ner_v2/mlTagger/models/'
    model=ner_v2.mlTagger.loadModel(modelPath)
    f_eval=model.f_eval;
    parameters=model.parameters;
    parameters['id_to_tag']=model.id_to_tag;


    #load dic, loadConceptTable 
    """
    dictFNames={"ac_cell":"./dlut/ner_v2/data/dict2/cell.txt.sort.token",
                "ac_mutation":"./dlut/ner_v2/data/dict2/mutation.txt.sort.token",
                "ac_phenotype":"./dlut/ner_v2/data/dict2/phenotype.txt.sort.token",
                "concept":"./dlut/ner_v2/data/concept/"};
    """
    dictFNames={"ac_cell":"./dlut/ner_v2/data/dict2/cell.txt.sort.token",
                "ac_phenotype":"./dlut/ner_v2/data/dict2/phenotype.txt.sort.token",
                "concept":"./dlut/ner_v2/data/concept/"};
    #load normalization dic

    nordictFNames={"nor_w2v":"/home/BIO/luoling/precision_medicine/NER/word2vec_model/medline_chemdner_pubmed_biov5_drug.token4_d50",
                   "nor_ec_gene":"./dlut/ner_v2/data/nor_data2/entity_vec_dic/gene_vec.txt",
                   "nor_ec_disease":"./dlut/ner_v2/data/nor_data2/entity_vec_dic/disease_vec.txt",
                   "nor_ec_drug":"./dlut/ner_v2/data/nor_data2/entity_vec_dic/chemical_vec.txt",
                   "nor_sim":"./dlut/ner_v2/data/nor_data2/memory_sim_dic.txt",
                   "nor_nosim":"./dlut/ner_v2/data/nor_data2/memory_nosim_dic.txt",
                   "nor_cid_all":"./dlut/ner_v2/data/nor_data2/CID_dic2/all_concept_CID.txt",
                   "nor_cid_drug":"./dlut/ner_v2/data/nor_data2/CID_dic/chemical.txt",
                   "nor_cid_phenotype":"./dlut/ner_v2/data/nor_data2/CID_dic/phenotype.txt",
                   "nor_cid_disease":"./dlut/ner_v2/data/nor_data2/CID_dic/disease.txt",
                   "nor_cid_cell":"./dlut/ner_v2/data/nor_data2/CID_dic/cell.txt",
                   "nor_cid_gene":"./dlut/ner_v2/data/nor_data2/CID_dic/gene.txt",
                   "nor_cid_mutation":"./dlut/ner_v2/data/nor_data2/CID_dic2/mutation.txt",
                   "nor_token_entity":"./dlut/ner_v2/data/nor_data2/Token2Entity_dic.txt"}

    dicts=ner_v2.go.loadExternalDicts(dictFNames);
    #nor_dicts=ner.normalize_main_v1.loadDicts(nordictFNames)
    nor_dicts=ner_v2.normalize_main_v2.loadDicts(nordictFNames)

    #load tmvar cid to rsid map
    tmvarFNames={"cidrcvF":"./dlut/ner_v2/MR_tmVarSoftware/mapping/mutation_withCID",
                 "rsidrcvF":"./dlut/ner_v2/MR_tmVarSoftware/mapping/variant_mapping_rsid2rcv.txt" }

    tmvar_dicts = ner_v2.tmVaro2fo.load_tmvarmap(tmvarFNames)
    

    #load relation extraction model 
    reDir = './dlut/relation/'
    #reModelFName = reDir + 'data/liver.in.train.h5'
    #reModelFName = reDir + 'data/lstm-resnet-luo-old.model.test'
    reModelFName = reDir + 'data/lstm-resnet-luo-new.model'
    relationModel,relationRep=relation.load_model(reModelFName,reDir);

#}}}

    def relation_fn(data,isPlain=True):
#{{{
        """
            call relation module to get relation extraction result. 
            @param:
                data:       dict. such as {'abstract':abstract,'entity_list':entity_list}
                isPlain:    determine whether return plain result or formated result for visual.
            @return:
                isPlain is false, return list. such as [relation1,relation2,...]
                isPlain is true, return string.
        """ 
        #avoid data is empty 
        print 'relation_fn...............'
        #print data

        if data:
            abstract=data['abstract'];
            entity_list=data['entity_list'];
            #utf-8 convert 
            if not isinstance(abstract,unicode):
                print "!WARNING!, input string not utf-8, we will convert it to utf-8";
                abstract=abstract.decode('utf-8');
            result=relation.run(abstract,entity_list,relationModel,relationRep);

            # print '@@@@@@@@@@@@@@@@@@'
            # print result
            # print type(result)
            # print '@@@@@@@@@@@@@@@@@@'

            if not isPlain:
                if len(result) < 3:
                    return []
                return result[2];
            else:
                result=relation.toJson(result[0],result[1]);
                return result;
        else:
            return '';
#}}}
    def ner_fn(data,isPlain=True):
#{{{
        """ 
            call ner module to get ner result.
            @param:
                data:       dict,such as {'abstract':abstract} 
                isPlain:    determine whether return plain result or formated result for visual.
            @return:
                isPlain is true, return string.
                isPlain is false, return list.  for more info, see parseAbstractEntityList method
        """
        abstract=data['abstract'];
        #utf-8 convert 
        if not isinstance(abstract,unicode):
            print "!WARNING!, input string not utf-8, we will convert it to utf-8";
            abstract=abstract.decode('utf-8');
      
	#print data
	#print 'ori:',abstract 
        result= ner_v2.go.go_fn(abstract,dicts,nor_dicts,tmvar_dicts,f_eval,parameters,True,True,isPlain);
       
        if isPlain:
            # nerResultPlainList=ner.go.parseAbstractEntityList(result);
            # print '@@@@@@@'
            # print nerResultPlainList
            # print '@@@@@@@'
            # print result
            # print '@@@@@@@@@@'
            return result;
        else:
            #parse plain string  ner result to create struct ner result 
            nerResultPlainList=ner_v2.go.parseAbstractEntityList(result);
            # print '@@@@@@@@'
            # print nerResultPlainList
            # print '@@@@@@@@'
            return nerResultPlainList;

    #}}}
    def nerRelation_fn(data,isPlain=True):
#{{{
        """ 
            delegate function to relation_fn and ner_fn to get ner result and relation extraction result.
            @param:
                data:       dict. such as {'abstract':abstract}
                isPlain:    determine whether return plain result or formated result for visual.
            @return:
                result:     a tuple object. such as (nerResult,relationResult).
                                each result is string.
        """
        #recognize named entity html_visu_nor_fn
        nerResultPlain=ner_fn(data,False);
        #parse plain string  ner result to create struct ner result 
        #nerResultPlainList=ner.go.parseAbstractEntityList(nerResultPlain);
        #get ner result contain html code
        if not isPlain:
            nerResult=nerResultPlain;
        else:
            #for some reason, html_visu_nor_fn method only accept string input 
            #so we will dump struct nerResult to string.
            import StringIO;
            nerResultStr=StringIO.StringIO();
            for elem in nerResultPlain:
                #write abstract
                nerResultStr.write(elem['abstract']+'\n');
                #write entity_list
                nerResultStr.write('\n'.join(['\t'.join(map(str,s)) for s in elem['entity_list']]));
                nerResultStr.write('\n');
            nerResultStr.write('\n');
            nerResultStr=nerResultStr.getvalue();
            #logger.debug('nerResultStr:\n{}'.format(nerResultStr));
            nerResult=ner_v2.html_visualization.html_visu_nor_fn(nerResultStr);

        #first doc to do relation extraction 
        #avoid empty list leading out of index error
        if len(nerResultPlain) ==0:
            nerResultPlain=[[]];
        relationResult=relation_fn(nerResultPlain[0],isPlain);
        return nerResult,relationResult;
#}}}
    
    def allFile(data, isPlain=True):
        
        ner_result = ner_fn(data, False)

        print type(ner_result)
        print ner_result
        print type(ner_result[0])

        # return ner_result[0]['entity_list']

        ''' temporary change '''
        relation_result = relation_fn(ner_result[0], False)

        print type(relation_result)

        if len(relation_result) == 0:
            ner_result[0]['triple_list'] = 'no relation'
            return ner_result


        ner_result[0]['triple_list'] = relation_result
        ner_result[0]['end_tag'] = 'END'
        print 'allFile:.......'
        print ner_result

        return ner_result

    def allResult(data,isPlain=True):
#{{{
        """
            generate all possible result. 
            @param:
                data:       dict. such as {'abstract':abstract}
                isPlain:    not used. just be in line with others.
            @return:
                result:     a tuple object. such as {nerResult,nerResultPlain,relationResult,relationResultPlain}.
        """
        #recognize named entity html_visu_nor_fn
        nerResultPlain=ner_fn(data,False);
        #get ner result contain html code
        import StringIO;
        nerResultStr=StringIO.StringIO();
        for elem in nerResultPlain:
            #write abstract
            nerResultStr.write(elem['abstract']+'\n');
            #write entity_list
            nerResultStr.write('\n'.join(['\t'.join(s) for s in elem['entity_list']]));
            nerResultStr.write('\n');
        nerResult=ner_v2.html_visualization.html_visu_nor_fn(nerResultStr)

        #first doc to do relation extraction 
        #avoid empty list leading out of index error
        if len(nerResultPlain) ==0:
            nerResultPlain=[[]];
        #for some reason, relation.run method can not allow we a pipeline,
        #so we have to call relation_fn twice
        relationResult=relation_fn(nerResultPlain[0]);
        relationResultPlain=[];
        for elem in nerResultPlain:
            relationResultPlain.append(relation_fn(elem,False));
        #result=json.dumps({'ner':nerResult,'relation':relationResult});
        return nerResult,nerResultPlain,relationResult,relationResultPlain;
#}}}
    def processCallback(data):
#{{{
        """
        according to client cmd to call function.
        @param:
            data:       string. NOTE: this is json format string. 
        @return:
            result:     json format string.
        """
        data=json.loads(data);
        cmd=data['cmd'];
        if cmd == 'ner':
            return  json.dumps({'ner':ner_fn(data,True)});
        elif cmd == 'ner_file':
            return  json.dumps(ner_fn(data,False));
        elif cmd == 'relation':
            return json.dumps({'relation':relation_fn(data,True)});
        elif cmd == 'relation_file':
            return json.dumps(relation_fn(data,False));
        elif cmd == 'all_file':
            return json.dumps(allFile(data))
        elif cmd == 'ner_relation':
            nerResult,relationResult=nerRelation_fn(data,True);
            return json.dumps({'ner':nerResult,'relation':relationResult});
        elif cmd == 'ner_relation_file':
            nerResult,nerResultPlain,relationResult,relationResultPlain=allResult(data);
            return json.dumps({'ner_file':nerResultPlain,'relation_file':relationResultPlain});
        elif cmd == 'all_result':
            nerResult,nerResultPlain,relationResult,relationResultPlain=allResult(data);
            return json.dumps({'ner':nerResult,'ner_file':nerResultPlain,'relation':relationResult,'relation_file':relationResultPlain});
        pass;
#}}}

    #listen to port
    PORT=14343;
    #address=('localhost',PORT)
    address=('192.168.2.83',PORT)
    server=TaggerServer(address,tagger_fn=processCallback);

    #Serve requests until CTRL+c is pressed
    try:
        asyncore_epoll.loop(poller=asyncore_epoll.epoll_poller)
    except KeyboardInterrupt:
        pass;

    #Close the server
    #server.close();
    #loop.run_until_complete(server.wait_closed());
    #loop.close()
