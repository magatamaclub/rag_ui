
import React, { useEffect } from 'react';
import { Form, Input, Button, message, Card } from 'antd';

const DifyConfigPage: React.FC = () => {
  const [form] = Form.useForm();

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const response = await fetch('/api/v1/dify-config');
        if (response.ok) {
          const data = await response.json();
          form.setFieldsValue(data);
        } else if (response.status === 404) {
          message.info("Dify configuration not found. Please set it up.");
        } else {
          message.error("Failed to fetch Dify configuration.");
        }
      } catch (error) {
        console.error("Error fetching Dify config:", error);
        message.error("Network error or server issue when fetching Dify config.");
      }
    };
    fetchConfig();
  }, [form]);

  const onFinish = async (values: any) => {
    try {
      const response = await fetch('/api/v1/dify-config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(values),
      });

      if (response.ok) {
        message.success("Dify configuration saved successfully!");
      } else {
        message.error("Failed to save Dify configuration.");
      }
    } catch (error) {
      console.error("Error saving Dify config:", error);
      message.error("Network error or server issue when saving Dify config.");
    }
  };

  return (
    <Card title="Dify API Configuration" style={{ maxWidth: 600, margin: '24px auto' }}>
      <Form
        form={form}
        layout="vertical"
        onFinish={onFinish}
        initialValues={{
          api_url: '',
          api_key: '',
        }}
      >
        <Form.Item
          label="Dify API URL"
          name="api_url"
          rules={[{ required: true, message: 'Please input your Dify API URL!' }]}
        >
          <Input placeholder="e.g., http://dify.go3daddy.com/v1" />
        </Form.Item>

        <Form.Item
          label="Dify API Key"
          name="api_key"
          rules={[{ required: true, message: 'Please input your Dify API Key!' }]}
        >
          <Input.Password placeholder="Your Dify API Key" />
        </Form.Item>

        <Form.Item>
          <Button type="primary" htmlType="submit">
            Save Configuration
          </Button>
        </Form.Item>
      </Form>
    </Card>
  );
};

export default DifyConfigPage;
