from sqlalchemy import or_, and_
from models import *
from forms import *

""" methods for reports """

def get_report(jobs):
    """ generate report details """

    data = {}         
    data['sf']=get_total_square_feet(jobs)
    data['total_cutouts']=get_cutouts_count(jobs)
    data['lf'] = get_edge_totals(jobs)
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
