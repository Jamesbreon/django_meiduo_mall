from goods.models import GoodsChannel


def get_categories():
    """
    {
        'gruop_id':{
            'channel': [cat1(手机), cat1(相机), cat1(数码)]
            'sub_cats':[cat2(手机通讯)， cat2(运营商)]
        }
    }

    """
    # 商品分类
    #  查询出所有商品频道数据并且按照组号和列号进行排序
    categories = {}
    group_channels_qs = GoodsChannel.objects.order_by('group_id', 'sequence')
    for channel in group_channels_qs:
        # 获取到商品id
        group_id = channel.group_id
        if group_id not in categories:
            categories[group_id] = {'channels': [], 'sub_cats': []}
        # 获取一级分类，然后放入到channel类表中
        cat1 = channel.category
        categories[group_id]['channels'].append(cat1)
        cat1.url = channel.url

        # 根据parent_id查询到所有的二级分类

        sub_cats_qs = cat1.subs.all()
        for cat2 in sub_cats_qs:
            # 得到第三级查询集
            cat3_qs = cat2.subs.all()
            # 把二级下面的所有三级绑定给cat2对象的cat_subs属性
            cat2.sub_cats = cat3_qs
            categories[group_id]['sub_cats'].append(cat2)
    return categories
