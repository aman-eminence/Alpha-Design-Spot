from rest_framework import serializers
from django.utils import timezone

from account.models import CustomerFrame
from .models import (
    Category, Post, Event, OtherPost, CustomerPostFrameMapping, CustomerOtherPostFrameMapping,
    BusinessPost, BusinessPostFrameMapping, BusinessCategory
)


class SubcategorySerializer(serializers.ModelSerializer):
    banner_image = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'banner_image']

    def get_banner_image(self, obj):
        request = self.context.get('request')
        if obj.banner_image:
            return request.build_absolute_uri(obj.banner_image.url)
        return None
        

class CategorySerializer(serializers.ModelSerializer):
    sub_categories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'sub_category', 'sub_categories', 'banner_image', 'is_active', 'is_featured']

    def get_sub_categories(self, obj):
        if not self.context.get('exclude_main_categories'):
            sub_categories = Category.objects.filter(sub_category=obj)
            serializer = SubcategorySerializer(sub_categories, many=True, context=self.context)
            return serializer.data
        return []
    

class BusinessCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BusinessCategory
        fields = [
            'id', 'profession_type', 'name', 'thumbnail'
        ]
        
    
    # def validate_name(self, value):
    #     if BusinessCategory.objects.filter(name__icontains=value).exists():
    #         raise serializers.ValidationError("A BusinessCategory with this name already exists.")
    #     return value


class SubCategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'name', 'banner_image', 'is_active', 'is_featured']

   
class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ['id', 'name', 'event_date', 'event_type', 'thumbnail']
        
    def validate_event_date(self, value):
        if value and value < timezone.now().date():
            raise serializers.ValidationError("Event date cannot be in the past.")
        return value
        

class PostSerializer(serializers.ModelSerializer):
    group_name = serializers.SerializerMethodField()
    event_details = serializers.SerializerMethodField()
    customer_details = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'event', 'file_type', 'file', 'group', 'added_on',
                  'group_name', 'customer_details', 'event_details']

    def get_customer_details(self, obj):
        request = self.context.get('request')
        frames = CustomerFrame.objects.select_related('customer', 'group').filter(customer=request.user, group__name=obj.group.name)
        urls = [request.build_absolute_uri(frame.frame_img.url) for frame in frames]
        return urls
        

    def get_group_name(self, obj):
        return obj.group.name if obj.group else None

    def get_event_details(self, obj):
        request = self.context.get('request')
        event = obj.event

        event_details = {
            "id": event.id,
            "name": event.name,
            "date": event.event_date,
        }

        if event.thumbnail:
            event_details["thumbnail"] = request.build_absolute_uri(event.thumbnail.url)

        return event_details

    
class OtherPostSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    group_name = serializers.CharField(source="group.name", read_only=True)
    
    class Meta:
        model  = OtherPost
        fields = ['id', 'category', 'category_name', 'file_type', 'file', 'group', 'group_name']
    
    
class BusinessPostSerializer(serializers.ModelSerializer):
    group_name = serializers.CharField(source="group.name", read_only=True)
    customer_details = serializers.SerializerMethodField()
    business_category_name = serializers.CharField(source="business_category.name", read_only=True)
    thumbnail = serializers.FileField(source="business_category.thumbnail", read_only=True)
    
    class Meta:
        model = BusinessPost
        fields = [
            'id', 'business_category', 'profession_type', 'file_type', 'file', 'group', 'added_on',
            'group_name', 'customer_details', 'business_category_name', 'thumbnail'
        ]

    def get_customer_details(self, obj):
        request = self.context.get('request')
        frames = CustomerFrame.objects.select_related('customer', 'group').filter(customer=request.user, group__name=obj.group.name)
        urls = [request.build_absolute_uri(frame.frame_img.url) for frame in frames]
        return urls
        

class CustomerPostFrameMappingSerializer(serializers.ModelSerializer):
    post_image = serializers.FileField(source="post.file", read_only=True)
    frame_image= serializers.FileField(source="customer_frame.frame_img", read_only=True)
    customer_number = serializers.SerializerMethodField(read_only=True)
    is_a_group = serializers.SerializerMethodField()
    event_name = serializers.SerializerMethodField()
    

    class Meta:
        model = CustomerPostFrameMapping
        fields = [
            'id', 'customer', 'customer_number', 'post', 'customer_frame', 'is_downloaded', 'post_image',
            'frame_image', 'is_a_group', 'event_name'
        ]
        
    def get_customer_number(self,obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.whatsapp_number
        return None
    
    def get_is_a_group(self, obj):
        if obj.customer_frame.group.name == "a" or "A":
            return "True"
        else:
            return "False"
        
    def get_event_name(self, obj):
        return obj.post.event.name
    
    
class CustomerOtherPostFrameMappingSerializer(serializers.ModelSerializer):
    post_image = serializers.FileField(source="other_post.file", read_only=True)
    frame_image= serializers.FileField(source="customer_frame.frame_img", read_only=True)
    is_a_group = serializers.SerializerMethodField()
    
    class Meta:
        model = CustomerOtherPostFrameMapping
        fields = [
            'id', 'customer', 'other_post', 'customer_frame', 'is_downloaded', 'post_image', 'frame_image',
            'is_a_group'
        ]
        
    
    def get_is_a_group(self, obj):
        if obj.customer_frame.group.name == "a" or "A":
            return True
        else:
            return False
               
        
class BusinessPostFrameMappingSerializer(serializers.ModelSerializer):
    post_image = serializers.FileField(source="post.file", read_only=True)
    frame_image= serializers.FileField(source="customer_frame.frame_img", read_only=True)
    customer_number = serializers.SerializerMethodField(read_only=True)
    is_a_group = serializers.SerializerMethodField()

    class Meta:
        model = BusinessPostFrameMapping
        fields = [
            'id', 'customer', 'customer_number', 'post', 'customer_frame', 'is_downloaded', 'post_image',
            'frame_image', 'is_a_group'
        ]
        
    def get_customer_number(self,obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return request.user.whatsapp_number
        return None
    
    def get_is_a_group(self, obj):
        if obj.customer_frame.group.name == "a" or "A":
            return "True"
        else:
            return "False"