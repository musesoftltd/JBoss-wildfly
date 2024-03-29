'''
Created on 20 Oct 2016

@author: ...
'''

from environmentProperties.allEnvs.propertiesPega import dictionary as globalDictionary
from library.auditing.auditingLibrary import auditObjectAtom, \
    auditObjectMolecule, reportingObject, auditObjectAtoms
from library.jboss.jbossLibrary import getAllDataSources, connectSilent
from library.pega.auditServers_basePega import auditServersBasePega
from library.util import scatterThread, gatherThreads


def auditServersMarketingThread(environment, servername, propertiesDictionary, bApplyRequiredChanges) :
    # merge global properties into dict - deliberately overwriting local with global dict all values
    runtimeProperties = dict()
    runtimeProperties.update(globalDictionary)
    runtimeProperties.update(propertiesDictionary)

    if connectSilent(servername, runtimeProperties["username"], runtimeProperties["password"]) == None:
        return
       
    ##############################################################
    # Base server audit...
    ##############################################################
    auditServersBasePega(environment, servername, runtimeProperties, bApplyRequiredChanges)
    
    ##############################################################
    # OO based auditing atoms - automatically reported on...
    ##############################################################
    auditObjectAtoms.append(auditObjectAtom(servername, runtimeProperties["username"], runtimeProperties["password"], "App: prsysmgmt Version", "/deployment=prsysmgmt_jboss.ear/", "content", runtimeProperties["prsysmanageVersionHash"], False))
    auditObjectAtoms.append(auditObjectAtom(servername, runtimeProperties["username"], runtimeProperties["password"], "App: PRPC Version", "/deployment=prpc_j2ee14_jboss61JBM.ear/", "content", runtimeProperties["prpcVersionHash"], False))
    
    
    bAllMustPass = True
    AllDatasources = getAllDataSources(servername, runtimeProperties["username"], runtimeProperties["password"])
    if (AllDatasources) :
        auditObjectMolecule1 = auditObjectMolecule("JDBC URL", servername, bAllMustPass)
        for ds in AllDatasources:
            auditObjectMolecule1.auditObjectAtoms.append(auditObjectAtom(servername, runtimeProperties["username"], runtimeProperties["password"], "JDBC URL - Marketing - " + ds, "/subsystem=datasources/data-source=" + ds + "/", "connection-url", runtimeProperties["targetDSUrlMarketing"], bApplyRequiredChanges))

def auditServersMarketing(environment, servers, propertiesDictionary, bApplyRequiredChanges) :
    # merge global properties into dict - deliberately overwriting local with global dict all values
    
    strThreadPoolId = "auditServersMarketing"    
    for servername in servers:
        # Create new threads
        scatterThread(strThreadPoolId, auditServersMarketingThread, args=(environment, servername, propertiesDictionary, bApplyRequiredChanges))
        
    gatherThreads(strThreadPoolId)

    for servername in servers:
        reportingObject.auditReport(environment, servername)
