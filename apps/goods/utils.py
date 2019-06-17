
def get_breadcrumb(category):
    # 通过cat3 找到cat2
    cat1 = category.parent.parent
    # cat1中没有url属性，因此动态生成
    cat1.url = cat1.goodschannel_set.all()[0].url
    breadcrumb = {
        'cat1': cat1,
        'cat2': category.parent,
        'cat3': category
    }

    return breadcrumb
