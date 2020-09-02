from sqlalchemy import or_, and_
from models import *
from forms import *
from datetime import datetime, timedelta
""" methods for reports """




def get_report(jobs):
    """ generate report details """

    data = {}         
    data['sf']=get_total_square_feet(jobs)
    data['total_cutouts']=get_cutouts_count(jobs)
    data['lf'] = get_edge_totals(jobs)
    data['contractors']=get_contractor_sf_totals(jobs)
    data['slab_types']=get_jobs_slab_type_totals(jobs)
    data['lf_types']=get_edge_type_totals(jobs)
    data['waste']=get_waste(jobs)
    return data


def get_cutouts_count(jobs):
    """ get the number of cuouts based on cutout and total """
    total=0
    results = {}
    for job in jobs:
        cutouts= db.session.query(Cutout.name, JobCutout.cutout_count, JobCutout.id).filter(JobCutout.job_id == job.id).join(Cutout).all()
        for cutout in cutouts:
            if cutout.name in results.keys():
                results[cutout.name] = results[cutout.name] + cutout.cutout_count
                total = total + cutout.cutout_count
            else:
                results[cutout.name]=cutout.cutout_count
                total = total + cutout.cutout_count
    results['total']=total

    return results

def get_total_square_feet(jobs):
    """" get the total sqare feet """

    sf=0
    for job in jobs:
        sf= sf + job.square_feet

    return sf

def get_edge_totals(jobs):
    """" get tje total lf for each edge and total overall """

    total=0
    results = {}
    for job in jobs:
        edges = db.session.query(Edge.name, JobEdge.lf, Edge.type).filter(JobEdge.job_id == job.id).join(Edge).all()
        for edge in edges:
            if edge.name in results.keys():
                results[edge.name] = results[edge.name] + edge.lf
                total = total + edge.lf
            else:
                results[edge.name] = edge.lf
                total = total  + edge.lf
    results['total']=total

    return results

def get_contractor_sf_totals(jobs):
    """ get the total sf for each ontrctor/customer """

    total=0
    results = {}
    for job in jobs:
        if job.contractor.name in results.keys():
            results[job.contractor.name] = results[job.contractor.name] + job.square_feet
            total = total + job.square_feet
        else:
            results[job.contractor.name] = job.square_feet
            total = total + job.square_feet
    results['total']=total
    return results

def get_jobs_slab_type_totals(jobs):
    """ get all jos separated by slab type """
    total = 0
    results = {}
    for job in jobs:
        for slab in job.slabs:
            if slab.type.name in results.keys():
                results[slab.type.name] = results[slab.type.name] + job.square_feet
                total = total  + job.square_feet
            else:
                results[slab.type.name] = job.square_feet
                total = total + job.square_feet
    results['total']=total
    return results

def total_lf_job(jobs):
    """ get total lf for each job """
    results = {}
    total=0
    for job in jobs:
        edges = JobEdge.query.filter(JobEdge.job_id==job.id).all()
        for edge in edges:
            total = total + edge.lf
        results[job.id]=total
    
    return results
        
def get_edge_type_totals(jobs):
    """" get tje total lf for each edge and total overall """

    total=0
    results = {}
    for job in jobs:
        edges = db.session.query(Edge.name, JobEdge.lf, Edge.type).filter(JobEdge.job_id == job.id).join(Edge).all()
        for edge in edges:
            if edge.type in results.keys():
                results[edge.type] = results[edge.type] + edge.lf
                total = total + edge.lf
            else:
                results[edge.type] = edge.lf
                total = total  + edge.lf
    results['total']=total

    return results

def get_waste(jobs):
    """ get the amount of wasted Material """
    results = {}
    results['total'] = 0
    results['Material Used'] = 0
    for job in jobs:
        for slab in job.slabs:
            if (slab.completed):
                slabjobs = db.session.query(SlabJob).filter(SlabJob.slab_id == slab.label).all()
                for slabjob in slabjobs:
                    results['Material Used'] = results['Material Used'] + slabjob.job_sf
                results['total'] = results['total'] + slab.calculate_area()
    if results['total'] != 0:
        results['Waste'] = results['total'] - results['Material Used']
        results['percent'] = round((results['Waste']/results['total']) * 100,2)
    return results