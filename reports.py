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
    data['slat_types']=get_jobs_slab_type_totals(jobs)
    return data


def get_cutouts_count(jobs):
    """ get the number of cuouts based on cutout and total """

    results = {'total': 0}
    for job in jobs:
        cutouts= db.session.query(Cutout.name, JobCutout.cutout_count, JobCutout.id).filter(JobCutout.job_id == job.id).join(Cutout).all()
        for cutout in cutouts:
            if cutout.name in results.keys():
                results[cutout.name] = results[cutout.name] + cutout.cutout_count
                results['total'] = results['total'] + cutout.cutout_count
            else:
                results[cutout.name]=cutout.cutout_count
                results['total'] = results['total'] + cutout.cutout_count

    return results

def get_total_square_feet(jobs):
    """" get the total sqare feet """

    sf=0
    for job in jobs:
        sf= sf + job.square_feet

    return sf

def get_edge_totals(jobs):
    """" get tje total lf for each edge and total overall """

    results = {'total': 0}
    for job in jobs:
        edges = db.session.query(Edge.name, JobEdge.lf, Edge.type).filter(JobEdge.job_id == job.id).join(Edge).all()
        for edge in edges:
            if edge.name in results.keys():
                results[edge.name] = results[edge.name] + edge.lf
                results['total'] = results['total'] + edge.lf
            else:
                results[edge.name] = edge.lf
                results['total'] = results['total'] + edge.lf

    return results

def get_contractor_sf_totals(jobs):
    """ get the total sf for each ontrctor/customer """

    results = {'total': 0}
    for job in jobs:
        if job.contractor.name in results.keys():
            results[job.contractor.name] = results[job.contractor.name] + job.square_feet
            results['total'] = results['total'] + job.square_feet
        else:
            results[job.contractor.name] = job.square_feet
            results['total'] = results['total'] + job.square_feet
    return results

def get_jobs_slab_type_totals(jobs):
    """ get all jos separated by slab type """

    results = {'total': 0}
    for job in jobs:
        for slab in job.slabs:
            if slab.type.name in results.keys():
                results[slab.type.name] = results[slab.type.name] + job.square_feet
                results['total'] = results['total'] + job.square_feet
            else:
                results[job.contractor.name] = job.square_feet
                results['total'] = results['total'] + job.square_feet

    return results