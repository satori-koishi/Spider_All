import json
from lxml import etree
from scrapy import Selector

token = 'uBgLy2zN88aTokllUWlyEZ2l6AK2k2dn'


def jilin_json_url_analysis(json_data, select_number, big='http://cx.jlsjsxxw.com', state=False, direct=False):
    project_html = json.loads(json_data.text)
    project_every = dict(project_html)
    url_list = []
    if project_every['tb']:
        html_tr = etree.HTML(project_every['tb'])
        tr = html_tr.xpath("//tr")
        if direct:
            return tr
        else:
            for every_tr in tr:
                p_u = every_tr.xpath('./td[%d]/a/@href' % select_number)[0]
                if not state:
                    url = p_u.replace('..', '')
                    url = big + url
                    url_list.append(url)
                else:
                    url_list.append(p_u)
            return url_list
    else:
        return url_list


class Project(object):
    """
    项目基本信息
    """
    __species = None
    __first_init = True

    def __new__(cls, *args, **kwargs):
        if cls.__species is None:
            cls.__species = object.__new__(cls)
        return cls.__species

    def __init__(self, companyName='', name='', code='', provinceCode='', area='', unit='', unitLicenseNum='',
                 catalog='', trait='', purpose='', money='', acreage='', level='', docuCode='',
                 token='uBgLy2zN88aTokllUWlyEZ2l6AK2k2dn',
                 projectSourceType='2'
                 ):
        """

        :param companyName:公司名称
        :param name:项目名称
        :param code:项目编号
        :param provinceCode:省级项目编号
        :param area:所在区划
        :param unit:建设单位
        :param unitLicenseNum:建设单位组织机构代码（统一社会信用代码）
        :param catalog:项目分类
        :param trait:建设性质
        :param purpose:工程用途
        :param money:总投资
        :param acreage:总面积
        :param level:立项级别
        :param docuCode:立项文号
        :param token:信息令牌
        """
        self.companyName = companyName
        self.name = name
        self.code = code
        self.provinceCode = provinceCode
        self.area = area
        self.unit = unit
        self.unitLicenseNum = unitLicenseNum
        self.catalog = catalog
        self.trait = trait
        self.purpose = purpose
        self.money = money
        self.acreage = acreage
        self.level = level
        self.docuCode = docuCode
        self.token = token
        self.projectSourceType = '2'

    def data(self):
        for k, v in self.__dict__.items():
            # print(k, v, '-----------------------')
            if v is None or (not v.split()):
                self.__dict__[k] = ''
            elif v and v.split():
                if v.split()[0] != '无' and v.split()[0] != '/' and v.split()[0] != '空':
                    self.__dict__[k] = v.split()[0]
                    if k == 'unitLicenseNum':
                        if len(self.__dict__[k]) != 18:
                            self.__dict__[k] = ''
                    if k.find('ate') != -1:
                        self.__dict__[k] = v.replace('/', '-')
            else:
                self.__dict__[k] = ''
        return self.__dict__


class Mark(object):
    """
    企业项目招投标信息
    """
    __species = None
    __first_init = True

    def __new__(cls, *args, **kwargs):
        if cls.__species is None:
            cls.__species = object.__new__(cls)
        return cls.__species

    def __init__(self, companyName='', code='', tenderNum='', provinceTenderNum='', tenderClass='',
                 tenderType='', tenderResultDate='', tenderMoney='', prjSize='', area='', agencyCorpName='',
                 agencyCorpCode='', tenderCorpName='', tenderCorpCode='', constructorName='',
                 constructorIDCard='', createDate='', token='uBgLy2zN88aTokllUWlyEZ2l6AK2k2dn',
                 projectSourceType='2'
                 ):
        """
        过滤

        :param companyName:企业名称
        :param code:项目编号
        :param tenderNum:中标通知书编号
        :param provinceTenderNum:省级中标通知书编号
        :param tenderClass:招标类型
        :param tenderType:招标方式
        :param tenderResultDate:中标日期
        :param tenderMoney:中标金额
        :param prjSize:建设规模
        :param area:面积（平方米）
        :param agencyCorpName:招标代理单位名称
        :param agencyCorpCode:招标代理单位组织机构代码
        :param tenderCorpName:中标单位名称
        :param tenderCorpCode:中标单位组织机构代码
        :param constructorName:项目经理/总监理工程师姓名
        :param constructorIDCard:项目经理/总监理工程师证件号码
        :param createDate:记录登记时间
        :param token:信息令牌
        """
        self.companyName = companyName
        self.code = code
        self.tenderNum = tenderNum
        self.provinceTenderNum = provinceTenderNum
        self.tenderClass = tenderClass
        self.tenderType = tenderType
        self.tenderResultDate = tenderResultDate
        self.tenderMoney = tenderMoney
        self.prjSize = prjSize
        self.area = area
        self.agencyCorpName = agencyCorpName
        self.agencyCorpCode = agencyCorpCode
        self.tenderCorpName = tenderCorpName
        self.tenderCorpCode = tenderCorpCode
        self.constructorName = constructorName
        self.constructorIDCard = constructorIDCard
        self.createDate = createDate
        self.token = token
        self.projectSourceType = projectSourceType

    def data(self):
        for k, v in self.__dict__.items():
            if v is None:
                self.__dict__[k] = ''
            elif v and v.split():
                if v.split()[0] != '无' and v.split()[0] != '/' and v.split()[0] != '空':
                    self.__dict__[k] = v.split()[0]
                    if k == 'unitLicenseNum':
                        if len(self.__dict__[k]) != 18:
                            self.__dict__[k] = ''
                    if k.find('ate') != -1:
                        self.__dict__[k] = v.replace('/', '-')
            else:
                self.__dict__[k] = ''
        return self.__dict__


class Contract(object):
    """
    json格式企业项目合同备案信息
    """
    __species = None
    __first_init = True

    def __new__(cls, *args, **kwargs):
        if cls.__species is None:
            cls.__species = object.__new__(cls)
        return cls.__species

    def __init__(self, companyName='', code='', recordNum='', provinceRecordNum='', contractNum='',
                 contractClassify='', contractType='', contractMoney='', prjSize='', contractDate='',
                 proprietorCorpName='',
                 proprietorCorpCode='', contractorCorpName='', contractorCorpCode='', unionCorpName='',
                 unionCorpCode='', createDate='',
                 token='uBgLy2zN88aTokllUWlyEZ2l6AK2k2dn', projectSourceType='2'
                 ):
        """
        过滤

        :param companyName:企业名称
        :param code:项目编号
        :param recordNum:合同备案编号
        :param provinceRecordNum:省级合同备案编号
        :param contractNum:合同编号
        :param contractClassify:合同分类
        :param contractType:合同类别
        :param contractMoney:合同金额
        :param prjSize:建设规模
        :param contractDate:合同签订日期
        :param proprietorCorpName:发包单位名称
        :param proprietorCorpCode:发包单位组织机构代码
        :param contractorCorpName:承包单位名称
        :param contractorCorpCode:承包单位组织机构代码
        :param unionCorpName:联合体承包单位名称
        :param unionCorpCode:联合体承包单位组织机构代码
        :param createDate:记录登记时间
        :param token:信息令牌
        """
        self.companyName = companyName
        self.code = code
        self.recordNum = recordNum
        self.provinceRecordNum = provinceRecordNum
        self.contractNum = contractNum
        self.contractClassify = contractClassify
        self.contractType = contractType
        self.contractMoney = contractMoney
        self.prjSize = prjSize
        self.contractDate = contractDate
        self.proprietorCorpName = proprietorCorpName
        self.proprietorCorpCode = proprietorCorpCode
        self.contractorCorpName = contractorCorpName
        self.contractorCorpCode = contractorCorpCode
        self.unionCorpName = unionCorpName
        self.unionCorpCode = unionCorpCode
        self.createDate = createDate
        self.token = token
        self.projectSourceType = projectSourceType

    def data(self):
        for k, v in self.__dict__.items():
            if v is None:
                self.__dict__[k] = ''
            elif v and v.split():
                if v.split()[0] != '无' and v.split()[0] != '/' and v.split()[0] != '空':
                    self.__dict__[k] = v.split()[0]
                    if k == 'unitLicenseNum':
                        if len(self.__dict__[k]) != 18:
                            self.__dict__[k] = ''
                    if k.find('ate') != -1:
                        self.__dict__[k] = v.replace('/', '-')
                else:
                    self.__dict__[k] = ''
            else:
                self.__dict__[k] = ''
        return self.__dict__


class MakeDrawing(object):
    """
    son格式企业项目施工图审查信息
    """
    __species = None
    __first_init = True

    def __new__(cls, *args, **kwargs):
        if cls.__species is None:
            cls.__species = object.__new__(cls)
        return cls.__species

    def __init__(self, companyName='', code='', censorCorpName='', censorCorpCode='', censorNum='',
                 provinceCensorNum='', censorEDate='', prjSize='', surveyCorpName='', surveyCorpCode='',
                 surveyCorpArea='',
                 designCorpName='', designCorpCode='', designCorpArea='', engineers='', stampNum='',
                 token='uBgLy2zN88aTokllUWlyEZ2l6AK2k2dn',
                 projectSourceType='2'):
        """
        过滤

        :param companyName:企业名称
        :param code:项目编号
        :param censorCorpName:合施工图审查机构名称
        :param censorCorpCode:施工图审查机构组织机构代码
        :param censorNum:施工图审查合格书编号
        :param provinceCensorNum:省级施工图审查合格书编号
        :param censorEDate:审查完成日期
        :param prjSize:建设规模
        :param surveyCorpName:勘察单位名称
        :param surveyCorpCode:勘察单位组织机构代码
        :param surveyCorpArea:勘察单位所在省份
        :param designCorpName:设计单位名称
        :param designCorpCode:设计单位组织机构代码
        :param designCorpArea:设计单位所在省份
        :param engineers:[{companyName[所在企业] , tradeName[专业名称] , prjDuty[担任角色] , name[姓名] , card[证件号码] , specialty[注册类型及等级] ,stampNum[执业印章号]},{......},{......},{......}]
        """
        self.companyName = companyName
        self.code = code
        self.censorCorpName = censorCorpName
        self.censorCorpCode = censorCorpCode
        self.censorNum = censorNum
        self.provinceCensorNum = provinceCensorNum
        self.censorEDate = censorEDate
        self.prjSize = prjSize
        self.surveyCorpName = surveyCorpName
        self.surveyCorpCode = surveyCorpCode
        self.surveyCorpArea = surveyCorpArea
        self.designCorpName = designCorpName
        self.designCorpCode = designCorpCode
        self.designCorpArea = designCorpArea
        self.engineers = engineers
        self.stampNum = stampNum
        self.projectSourceType = projectSourceType
        self.token = token

    def data(self):
        for k, v in self.__dict__.items():
            if v is None:
                self.__dict__[k] = ''
            elif k == 'engineers':
                if v:
                    self.__dict__[k] = v
                else:
                    self.__dict__[k] = []
            elif v and v.split():
                if v.split()[0] != '无' and v.split()[0] != '/' and v.split()[0] != '空':
                    self.__dict__[k] = v.split()[0]
                    if k == 'unitLicenseNum':
                        if len(self.__dict__[k]) != 18:
                            self.__dict__[k] = ''
                    if k.find('ate') != -1:
                        self.__dict__[k] = v.replace('/', '-')
                else:
                    self.__dict__[k] = ''
            else:
                self.__dict__[k] = ''
        return self.__dict__


class ConstructionPermit(object):
    """
    json格式企业项目施工许可信息
    """
    __species = None
    __first_init = True

    def __new__(cls, *args, **kwargs):
        if cls.__species is None:
            cls.__species = object.__new__(cls)
        return cls.__species

    def __init__(self, companyName='', code='', builderLicenceNum='', provinceBuilderLicenceNum='', censorNum='',
                 contractMoney='', area='', constructorName='', constructorIDCard='',
                 supervisionName='', supervisionIDCard='', econCorpName='', econCorpCode='', econCorpArea='',
                 designCorpName='', designCorpCode='', designCorpArea='', consCorpName='', consCorpCode='',
                 consCorpArea='', superCorpName='', superCorpCode='', superCorpArea='', createDate='',
                 token='uBgLy2zN88aTokllUWlyEZ2l6AK2k2dn', projectSourceType='2'
                 ):
        """

        :param companyName:企业名称
        :param code:项目编号
        :param builderLicenceNum:施工许可证编号
        :param provinceBuilderLicenceNum:省级施工许可证编号
        :param censorNum:施工图审查合格书编号
        :param contractMoney:合同金额(万元)
        :param area:面积（平方米）
        :param constructorName:项目经理名称
        :param constructorIDCard:项目经理证件号码
        :param supervisionName:总监理工程师名称
        :param supervisionIDCard:总监理工程师证件号码
        :param econCorpName:勘察单位名称
        :param econCorpCode:勘察单位组织机构代码
        :param econCorpArea:勘察单位所在省份
        :param designCorpName:设计单位名称
        :param designCorpCode:设计单位组织机构代码
        :param designCorpArea:设计单位所在省份
        :param consCorpName:施工单位名称
        :param consCorpCode:施工单位组织机构代码
        :param consCorpArea:施工单位所在省份
        :param superCorpName:监理单位名称
        :param superCorpCode:监理单位组织机构代码
        :param superCorpArea:监理单位所在省份
        :param createDate:监理单位组织机构代码
        # :param projectSourceType:项目信息来源类别(使用哪种code为主键,1为四库一平台项目编号,2为各省级编号)]
        # :param token:信息令牌
        """

        self.companyName = companyName
        self.code = code
        self.builderLicenceNum = builderLicenceNum
        self.provinceBuilderLicenceNum = provinceBuilderLicenceNum
        self.censorNum = censorNum
        self.contractMoney = contractMoney
        self.area = area
        self.constructorName = constructorName
        self.constructorIDCard = constructorIDCard
        self.supervisionName = supervisionName
        self.supervisionIDCard = supervisionIDCard
        self.econCorpName = econCorpName
        self.econCorpCode = econCorpCode
        self.econCorpArea = econCorpArea
        self.designCorpName = designCorpName
        self.designCorpCode = designCorpCode
        self.designCorpArea = designCorpArea
        self.consCorpName = consCorpName
        self.consCorpCode = consCorpCode
        self.consCorpArea = consCorpArea
        self.superCorpName = superCorpName
        self.superCorpCode = superCorpCode
        self.superCorpArea = superCorpArea
        self.createDate = createDate
        self.projectSourceType = projectSourceType
        self.token = token

    def data(self):
        for k, v in self.__dict__.items():
            if v is None:
                self.__dict__[k] = ''
            elif v and v.split():
                if v.split()[0] != '无' and v.split()[0] != '/' and v.split()[0] != '空':
                    self.__dict__[k] = v.split()[0]
                    if k == 'unitLicenseNum':
                        if len(self.__dict__[k]) != 18:
                            self.__dict__[k] = ''
                    if k.find('ate') != -1:
                        self.__dict__[k] = v.replace('/', '-')
                else:
                    self.__dict__[k] = ''
            else:
                self.__dict__[k] = ''
        return self.__dict__


class Completion(object):
    """
    json格式企业项目竣工验收备案信息
    """
    __species = None
    __first_init = True

    def __new__(cls, *args, **kwargs):
        if cls.__species is None:
            cls.__species = object.__new__(cls)
        return cls.__species

    def __init__(self, companyName='', code='', prjFinishNum='', provincePrjFinishNum='', factCost='',
                 factArea='', factSize='', prjStructureType='', factBeginDate='', factEndDate='',
                 createDate='', mark='', designCorpName='', designCorpCode='',
                 designCorpArea='', superCorpName='', superCorpCode='', superCorpArea='', consCorpName='',
                 consCorpCode='', consCorpArea='', constructorName='', constructorIDCard='', constructorSpecialty='',
                 constructorStampNum='', supervisionName='', supervisionIDCard='', supervisionSpecialty='',
                 supervisionStampNum='', token='uBgLy2zN88aTokllUWlyEZ2l6AK2k2dn', projectSourceType='2'
                 ):
        """
        过滤

        :param companyName:企业名称
        :param code:项目编号
        :param prjFinishNum:竣工备案编号
        :param provincePrjFinishNum:省级竣工备案编号
        :param factCost:实际造价（万元）
        :param factArea:实际面积（平方米）
        :param factSize:实际建设规模
        :param prjStructureType:结构体系]
        :param factBeginDate:实际开工日期
        :param factEndDate:实际竣工验收日期
        :param createDate:记录登记时间
        :param mark:备注
        :param designCorpName:设计单位名称
        :param designCorpCode:设计单位组织机构代码
        :param designCorpArea:设计单位所在省份
        :param superCorpName:监理单位名称
        :param superCorpCode:监理单位组织机构代码
        :param superCorpArea:监理单位所在省份
        :param consCorpName:施工单位名称
        :param consCorpCode:施工单位组织机构代码
        :param consCorpArea:施工单位所在省份
        :param constructorName:项目经理名称
        :param constructorIDCard:项目经理证件号码
        :param constructorSpecialty:项目经理注册类型及等级
        :param constructorStampNum:项目经理执业印章号
        :param supervisionName:总监理工程师名称
        :param supervisionIDCard:总监理工程师证件号码
        :param supervisionSpecialty:总监理工程师注册类型及等级
        :param supervisionStampNum:总监理工程师执业印章号
        """
        self.companyName = companyName
        self.code = code
        self.prjFinishNum = prjFinishNum
        self.provincePrjFinishNum = provincePrjFinishNum
        self.factCost = factCost
        self.factArea = factArea
        self.factSize = factSize
        self.prjStructureType = prjStructureType
        self.factBeginDate = factBeginDate
        self.factEndDate = factEndDate
        self.createDate = createDate
        self.mark = mark
        self.designCorpName = designCorpName
        self.designCorpCode = designCorpCode
        self.designCorpArea = designCorpArea
        self.superCorpName = superCorpName
        self.superCorpCode = superCorpCode
        self.superCorpArea = superCorpArea
        self.consCorpName = consCorpName
        self.consCorpCode = consCorpCode
        self.consCorpArea = consCorpArea
        self.constructorIDCard = constructorIDCard
        self.constructorName = constructorName
        self.constructorStampNum = constructorStampNum
        self.constructorSpecialty = constructorSpecialty
        self.supervisionName = supervisionName
        self.supervisionIDCard = supervisionIDCard
        self.supervisionSpecialty = supervisionSpecialty
        self.supervisionStampNum = supervisionStampNum
        self.projectSourceType = '2'
        self.token = token

    def data(self):
        for k, v in self.__dict__.items():
            if v is None:
                self.__dict__[k] = ''
            elif v and v.split():
                if v.split()[0] != '无' and v.split()[0] != '/' and v.split()[0] != '空':
                    self.__dict__[k] = v.split()[0]
                    if k == 'unitLicenseNum':
                        if len(self.__dict__[k]) != 18:
                            self.__dict__[k] = ''
                    if k.find('ate') != -1:
                        self.__dict__[k] = v.replace('/', '-')
                else:
                    self.__dict__[k] = ''
            else:
                self.__dict__[k] = ''
        return self.__dict__


class Projects(object):
    def __init__(self, project):
        if project == 'Project':
            project_dir = Project()
            self.data = project_dir.data()

        elif project == 'Mark':
            project_dir = Mark()
            self.data = project_dir.data()

        elif project == 'Contract':
            project_dir = Contract()
            self.data = project_dir.data()

        elif project == 'MakeDrawing':
            project_dir = MakeDrawing()
            self.data = project_dir.data()

        elif project == 'ConstructionPermit':
            project_dir = ConstructionPermit()
            self.data = project_dir.data()

        elif project == 'Completion':
            project_dir = Completion()
            self.data = project_dir.data()

    def html_analysis(self, response, attrs):
        for html in attrs:
            if html['that'] != '':
                self.data[html['name']] = Selector(response=response).xpath(html['attr'])[html['that']].xpath(
                    html['then']).extract_first()
            else:
                self.data[html['name']] = Selector(response=response).xpath(html['attr']).extract_first()
        return self.data

# xx = Projects('Project')
# cc = type('Project', (), {})
# print(cc.data())
# def html_analysis(response, attrs):
#     data = {}
#     for html in attrs:
#         if html['that']:
#             data[html['name']] = Selector(response=response).xpath(html['attr'])[html['that']].xpath(
#                 html['then']).extract_first()
#         else:
#             data[html['name']] = Selector(response=response).xpath(html['attr']).extract_first()
#     return data
