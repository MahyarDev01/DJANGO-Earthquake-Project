import numpy as np

def haversine_distance(lat1, lon1, lat2=35.6762, lon2=139.6503):
    """
    محاسبه فاصله جغرافیایی (کیلومتر) بین دو نقطه با فرمول Haversine
    مختصات پیش‌فرض مقصد: توکیو (35.6762N, 139.6503E)
    """
    R = 6371.0  # شعاع زمین به کیلومتر
    
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = np.sin(dlat / 2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2.0)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    return R * c